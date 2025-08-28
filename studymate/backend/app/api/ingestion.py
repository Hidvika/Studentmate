import asyncio
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import Document, Chunk
from app.s3.client import get_s3_client
from app.ingestion.extractor import PDFExtractor
from app.ingestion.normalizer import TextNormalizer
from app.ingestion.chunker import Chunker
from app.retrieval.embeddings import create_embeddings, serialize_embedding
from app.retrieval.index import FAISSIndex
from app.core.config import settings

router = APIRouter(prefix="/ingest", tags=["ingestion"])


class IngestionResponse(BaseModel):
    """Ingestion response model."""
    document_ids: List[str]
    status: str


class IngestionStatusResponse(BaseModel):
    """Ingestion status response model."""
    status: str
    stats: dict


# Global instances
extractor = PDFExtractor()
normalizer = TextNormalizer()
chunker = Chunker(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap
)
embeddings = create_embeddings()
faiss_index = FAISSIndex(dimension=embeddings.get_dimension())


async def process_document(
    file_data: bytes,
    filename: str,
    document_id: UUID,
    db: AsyncSession
) -> dict:
    """Process a single document through the full pipeline."""
    
    try:
        # Step 1: Extract text from PDF
        extracted_text, metadata = extractor.extract_text(file_data)
        
        # Step 2: Normalize text
        normalized_text = normalizer.normalize_text(
            extracted_text, 
            metadata.get("page_texts")
        )
        
        # Step 3: Chunk text
        chunks = chunker.chunk_text(
            normalized_text,
            filename=filename,
            page_texts=metadata.get("page_texts")
        )
        
        # Step 4: Generate embeddings
        chunk_texts = [chunk["text"] for chunk in chunks]
        chunk_embeddings = embeddings.embed_texts(chunk_texts)
        
        # Step 5: Store chunks in database
        db_chunks = []
        for i, (chunk, embedding) in enumerate(zip(chunks, chunk_embeddings)):
            db_chunk = Chunk(
                document_id=document_id,
                chunk_index=chunk["chunk_index"],
                start_word=chunk["start_word"],
                end_word=chunk["end_word"],
                page_start=chunk["page_start"],
                page_end=chunk["page_end"],
                text=chunk["text"],
                embedding_vector=serialize_embedding(embedding)
            )
            db.add(db_chunk)
            db_chunks.append(db_chunk)
        
        # Step 6: Update FAISS index
        faiss_index.upsert(document_id, chunk_embeddings, chunks)
        
        # Step 7: Update document status
        document = await db.get(Document, document_id)
        if document:
            document.status = "indexed"
        
        await db.commit()
        
        return {
            "status": "success",
            "pages": metadata.get("pages", 0),
            "chunks": len(chunks),
            "extractor": metadata.get("extractor", "unknown")
        }
        
    except Exception as e:
        # Update document status to failed
        document = await db.get(Document, document_id)
        if document:
            document.status = "failed"
            await db.commit()
        
        raise e


@router.post("/", response_model=IngestionResponse)
async def ingest_documents(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
) -> IngestionResponse:
    """Ingest multiple PDF documents."""
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Validate files
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail=f"File {file.filename} is not a PDF"
            )
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        max_size = settings.max_file_size_mb * 1024 * 1024
        if size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} is too large (max {settings.max_file_size_mb}MB)"
            )
    
    document_ids = []
    
    for file in files:
        try:
            # Read file data
            file_data = await file.read()
            
            # Create document record
            document = Document(
                filename=file.filename,
                s3_key="",  # Will be set after upload
                status="processing"
            )
            db.add(document)
            await db.flush()
            
            # Upload to S3
            s3_client = get_s3_client()
            s3_key = s3_client.upload_pdf(document.id, file.filename, file.file)
            document.s3_key = s3_key
            await db.flush()
            
            document_ids.append(str(document.id))
            
            # Process document asynchronously
            asyncio.create_task(
                process_document(file_data, file.filename, document.id, db)
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process {file.filename}: {str(e)}"
            )
    
    await db.commit()
    
    return IngestionResponse(
        document_ids=document_ids,
        status="accepted"
    )


@router.get("/{document_id}/status", response_model=IngestionStatusResponse)
async def get_ingestion_status(
    document_id: str,
    db: AsyncSession = Depends(get_db)
) -> IngestionStatusResponse:
    """Get ingestion status for a document."""
    
    try:
        stmt = select(Document).where(Document.id == UUID(document_id))
        result = await db.execute(stmt)
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get chunk count if indexed
        stats = {"pages": 0, "chunks": 0}
        if document.status == "indexed":
            stmt = select(Chunk).where(Chunk.document_id == document.id)
            result = await db.execute(stmt)
            chunks = result.scalars().all()
            stats["chunks"] = len(chunks)
            
            # Estimate pages from chunks
            if chunks:
                max_page = max(chunk.page_end for chunk in chunks)
                stats["pages"] = max_page
        
        return IngestionStatusResponse(
            status=document.status,
            stats=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get status: {str(e)}"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a document and all its chunks."""
    
    try:
        stmt = select(Document).where(Document.id == UUID(document_id))
        result = await db.execute(stmt)
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from S3
        s3_client = get_s3_client()
        s3_client.delete_document(document.id)
        
        # Delete from database (cascade will handle chunks)
        await db.delete(document)
        await db.commit()
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )
