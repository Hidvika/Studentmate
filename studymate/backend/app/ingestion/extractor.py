import io
import re
from typing import Any, Dict, List, Optional, Tuple

import fitz  # PyMuPDF
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from pypdf import PdfReader


class PDFExtractor:
    """PDF text extractor with PyMuPDF primary and pdfminer.six fallback."""
    
    def __init__(self) -> None:
        self.lap_params = LAParams(
            line_margin=0.5,
            word_margin=0.1,
            char_margin=2.0,
            boxes_flow=0.5,
            detect_vertical=True,
        )
    
    def extract_text(self, pdf_data: bytes) -> Tuple[str, Dict[str, Any]]:
        """Extract text from PDF with metadata.
        
        Returns:
            Tuple of (extracted_text, metadata)
        """
        # Try PyMuPDF first
        try:
            return self._extract_with_pymupdf(pdf_data)
        except Exception as e:
            # Fallback to pdfminer.six
            try:
                return self._extract_with_pdfminer(pdf_data)
            except Exception as fallback_e:
                raise RuntimeError(f"Both PyMuPDF and pdfminer failed: {e}, {fallback_e}")
    
    def _extract_with_pymupdf(self, pdf_data: bytes) -> Tuple[str, Dict[str, Any]]:
        """Extract text using PyMuPDF."""
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        
        metadata = {
            "pages": len(doc),
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "extractor": "pymupdf",
        }
        
        text_parts = []
        page_texts = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Get text blocks in reading order
            blocks = page.get_text("dict")
            page_text = ""
            
            # Sort blocks by vertical position (top to bottom)
            text_blocks = []
            for block in blocks["blocks"]:
                if "lines" in block:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text_blocks.append({
                                "text": span["text"],
                                "bbox": span["bbox"],
                                "font": span["font"],
                                "size": span["size"],
                            })
            
            # Sort by y-coordinate (top to bottom), then x-coordinate (left to right)
            text_blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
            
            # Reconstruct text
            for block in text_blocks:
                page_text += block["text"] + " "
            
            page_texts.append(page_text.strip())
            text_parts.append(page_text.strip())
        
        doc.close()
        
        full_text = "\n\n".join(text_parts)
        metadata["page_texts"] = page_texts
        
        return full_text, metadata
    
    def _extract_with_pdfminer(self, pdf_data: bytes) -> Tuple[str, Dict[str, Any]]:
        """Extract text using pdfminer.six."""
        # Get metadata with pypdf
        pdf_reader = PdfReader(io.BytesIO(pdf_data))
        metadata = {
            "pages": len(pdf_reader.pages),
            "title": pdf_reader.metadata.get("/Title", ""),
            "author": pdf_reader.metadata.get("/Author", ""),
            "subject": pdf_reader.metadata.get("/Subject", ""),
            "extractor": "pdfminer",
        }
        
        # Extract text with pdfminer
        output = io.StringIO()
        extract_text_to_fp(io.BytesIO(pdf_data), output, laparams=self.lap_params)
        text = output.getvalue()
        output.close()
        
        # Split into pages (approximate)
        lines = text.split("\n")
        page_texts = []
        current_page = []
        
        for line in lines:
            current_page.append(line)
            # Simple heuristic: long lines might indicate page breaks
            if len(line.strip()) < 10 and len(current_page) > 20:
                page_texts.append("\n".join(current_page))
                current_page = []
        
        if current_page:
            page_texts.append("\n".join(current_page))
        
        metadata["page_texts"] = page_texts
        
        return text, metadata
    
    def get_page_ranges(self, text: str, page_texts: List[str]) -> List[Tuple[int, int]]:
        """Estimate page ranges for text chunks.
        
        Returns list of (start_page, end_page) tuples for each chunk.
        """
        if not page_texts:
            return [(1, 1)]
        
        # Simple heuristic: split text into chunks and map to pages
        total_chars = len(text)
        chars_per_page = [len(page) for page in page_texts]
        total_page_chars = sum(chars_per_page)
        
        if total_page_chars == 0:
            return [(1, 1)]
        
        page_ranges = []
        current_pos = 0
        
        for i, page_chars in enumerate(chars_per_page):
            if current_pos >= total_chars:
                break
            
            start_pos = current_pos
            end_pos = min(current_pos + page_chars, total_chars)
            
            # Find the actual text boundaries
            start_idx = text.find(page_texts[i], start_pos)
            if start_idx != -1:
                end_idx = start_idx + len(page_texts[i])
                page_ranges.append((i + 1, i + 1))  # Page numbers are 1-indexed
                current_pos = end_idx
            else:
                page_ranges.append((i + 1, i + 1))
                current_pos += page_chars
        
        return page_ranges if page_ranges else [(1, 1)]
