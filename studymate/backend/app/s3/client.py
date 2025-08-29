import json
import os
from typing import Any, BinaryIO, Optional
from uuid import UUID

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from minio import Minio
from minio.error import S3Error

from app.core.config import settings


class S3Client:
    """S3/MinIO client wrapper for StudyMate file storage."""
    
    def __init__(self) -> None:
        self.bucket = settings.s3_bucket
        self.endpoint = settings.s3_endpoint
        
        # Use MinIO client for local development
        if "minio" in self.endpoint or "localhost" in self.endpoint:
            self.client = Minio(
                self.endpoint.replace("http://", "").replace("https://", ""),
                access_key=settings.s3_access_key,
                secret_key=settings.s3_secret_key,
                secure=False,
            )
            self._ensure_bucket_exists()
        else:
            # Use boto3 for AWS S3
            self.client = boto3.client(
                "s3",
                endpoint_url=self.endpoint,
                aws_access_key_id=settings.s3_access_key,
                aws_secret_access_key=settings.s3_secret_key,
                region_name=settings.s3_region,
            )
    
    def _ensure_bucket_exists(self) -> None:
        """Ensure the bucket exists (MinIO only)."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as e:
            raise RuntimeError(f"Failed to create bucket {self.bucket}: {e}")
    
    def upload_pdf(self, document_id: UUID, filename: str, file_data: BinaryIO) -> str:
        """Upload original PDF to S3.
        
        Returns the S3 key for the uploaded file.
        """
        s3_key = f"raw/{document_id}/{filename}"
        
        try:
            if hasattr(self.client, "put_object"):  # MinIO
                self.client.put_object(
                    self.bucket,
                    s3_key,
                    file_data,
                    length=os.fstat(file_data.fileno()).st_size,
                    content_type="application/pdf",
                )
            else:  # boto3
                self.client.upload_fileobj(
                    file_data,
                    self.bucket,
                    s3_key,
                    ExtraArgs={"ContentType": "application/pdf"},
                )
            
            return s3_key
        except (S3Error, ClientError) as e:
            raise RuntimeError(f"Failed to upload PDF {filename}: {e}")
    
    def upload_chunks(self, document_id: UUID, chunks: list[dict[str, Any]]) -> str:
        """Upload chunked text data to S3.
        
        Returns the S3 key for the chunks file.
        """
        s3_key = f"chunks/{document_id}/chunks.json"
        
        try:
            chunks_data = json.dumps(chunks, indent=2)
            
            if hasattr(self.client, "put_object"):  # MinIO
                self.client.put_object(
                    self.bucket,
                    s3_key,
                    chunks_data.encode("utf-8"),
                    length=len(chunks_data.encode("utf-8")),
                    content_type="application/json",
                )
            else:  # boto3
                self.client.put_object(
                    self.bucket,
                    s3_key,
                    chunks_data.encode("utf-8"),
                    ContentType="application/json",
                )
            
            return s3_key
        except (S3Error, ClientError) as e:
            raise RuntimeError(f"Failed to upload chunks for document {document_id}: {e}")
    
    def download_chunks(self, document_id: UUID) -> list[dict[str, Any]]:
        """Download chunked text data from S3."""
        s3_key = f"chunks/{document_id}/chunks.json"
        
        try:
            if hasattr(self.client, "get_object"):  # MinIO
                response = self.client.get_object(self.bucket, s3_key)
                chunks_data = response.read().decode("utf-8")
            else:  # boto3
                response = self.client.get_object(Bucket=self.bucket, Key=s3_key)
                chunks_data = response["Body"].read().decode("utf-8")
            
            return json.loads(chunks_data)
        except (S3Error, ClientError) as e:
            raise RuntimeError(f"Failed to download chunks for document {document_id}: {e}")
    
    def delete_document(self, document_id: UUID) -> None:
        """Delete all files associated with a document."""
        try:
            # Delete raw PDF
            raw_prefix = f"raw/{document_id}/"
            # Delete chunks
            chunks_prefix = f"chunks/{document_id}/"
            
            if hasattr(self.client, "list_objects"):  # MinIO
                # Delete raw files
                objects = self.client.list_objects(self.bucket, prefix=raw_prefix, recursive=True)
                for obj in objects:
                    self.client.remove_object(self.bucket, obj.object_name)
                
                # Delete chunk files
                objects = self.client.list_objects(self.bucket, prefix=chunks_prefix, recursive=True)
                for obj in objects:
                    self.client.remove_object(self.bucket, obj.object_name)
            else:  # boto3
                # Delete raw files
                paginator = self.client.get_paginator("list_objects_v2")
                for page in paginator.paginate(Bucket=self.bucket, Prefix=raw_prefix):
                    if "Contents" in page:
                        objects = [{"Key": obj["Key"]} for obj in page["Contents"]]
                        if objects:
                            self.client.delete_objects(Bucket=self.bucket, Delete={"Objects": objects})
                
                # Delete chunk files
                for page in paginator.paginate(Bucket=self.bucket, Prefix=chunks_prefix):
                    if "Contents" in page:
                        objects = [{"Key": obj["Key"]} for obj in page["Contents"]]
                        if objects:
                            self.client.delete_objects(Bucket=self.bucket, Delete={"Objects": objects})
        except (S3Error, ClientError) as e:
            raise RuntimeError(f"Failed to delete document {document_id}: {e}")


# Global instance
# Initialize S3 client lazily to avoid connection issues during import
s3_client = None

def get_s3_client():
    """Get or create S3 client instance."""
    global s3_client
    if s3_client is None:
        s3_client = S3Client()
    return s3_client
