import math
from typing import List, Tuple


class Chunker:
    """Text chunker with sliding window approach."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100) -> None:
        """Initialize chunker with specified parameters.
        
        Args:
            chunk_size: Number of words per chunk
            chunk_overlap: Number of words to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.stride = chunk_size - chunk_overlap  # 400 for default values
    
    def chunk_text(self, text: str, filename: str = "", page_texts: List[str] = None) -> List[dict]:
        """Chunk text into overlapping segments.
        
        Args:
            text: Input text to chunk
            filename: Source filename for metadata
            page_texts: List of page texts for page range estimation
            
        Returns:
            List of chunk dictionaries with metadata
        """
        if not text.strip():
            return []
        
        # Tokenize by whitespace into words
        words = text.split()
        
        if len(words) < self.chunk_size:
            # Single chunk for short texts
            return [{
                "chunk_index": 0,
                "start_word": 0,
                "end_word": len(words),
                "page_start": 1,
                "page_end": 1,
                "text": text.strip(),
                "source_filename": filename,
                "word_count": len(words)
            }]
        
        chunks = []
        chunk_index = 0
        
        # Calculate number of chunks
        num_chunks = self._calculate_num_chunks(len(words))
        
        for i in range(0, len(words), self.stride):
            start_word = i
            end_word = min(i + self.chunk_size, len(words))
            
            # Extract chunk text
            chunk_words = words[start_word:end_word]
            chunk_text = " ".join(chunk_words)
            
            # Estimate page range
            page_start, page_end = self._estimate_page_range(
                start_word, end_word, len(words), page_texts
            )
            
            chunk = {
                "chunk_index": chunk_index,
                "start_word": start_word,
                "end_word": end_word,
                "page_start": page_start,
                "page_end": page_end,
                "text": chunk_text,
                "source_filename": filename,
                "word_count": len(chunk_words)
            }
            
            chunks.append(chunk)
            chunk_index += 1
            
            # Stop if we've reached the end
            if end_word >= len(words):
                break
        
        return chunks
    
    def _calculate_num_chunks(self, num_words: int) -> int:
        """Calculate the number of chunks for a given number of words.
        
        Formula: ceil((N-500)/400)+1 for N≥500
        """
        if num_words < self.chunk_size:
            return 1
        
        return math.ceil((num_words - self.chunk_size) / self.stride) + 1
    
    def _estimate_page_range(self, start_word: int, end_word: int, total_words: int, 
                           page_texts: List[str] = None) -> Tuple[int, int]:
        """Estimate page range for a chunk based on word positions."""
        if not page_texts:
            return 1, 1
        
        # Calculate word positions as percentages
        start_percent = start_word / total_words if total_words > 0 else 0
        end_percent = end_word / total_words if total_words > 0 else 0
        
        # Map percentages to page numbers
        total_pages = len(page_texts)
        if total_pages == 0:
            return 1, 1
        
        # Calculate word counts per page for more accurate mapping
        page_word_counts = []
        for page_text in page_texts:
            page_words = page_text.split()
            page_word_counts.append(len(page_words))
        
        total_page_words = sum(page_word_counts)
        if total_page_words == 0:
            return 1, 1
        
        # Find start page
        current_word_count = 0
        start_page = 1
        for i, page_words in enumerate(page_word_counts):
            if current_word_count + page_words > start_word:
                start_page = i + 1
                break
            current_word_count += page_words
        else:
            start_page = total_pages
        
        # Find end page
        current_word_count = 0
        end_page = 1
        for i, page_words in enumerate(page_word_counts):
            if current_word_count + page_words > end_word:
                end_page = i + 1
                break
            current_word_count += page_words
        else:
            end_page = total_pages
        
        return start_page, end_page
    
    def validate_overlap(self, chunks: List[dict]) -> bool:
        """Validate that chunks have correct overlap.
        
        Returns True if overlap is correct, False otherwise.
        """
        if len(chunks) < 2:
            return True
        
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]
            next_chunk = chunks[i + 1]
            
            # Check that last 100 words of current chunk == first 100 words of next chunk
            current_words = current_chunk["text"].split()
            next_words = next_chunk["text"].split()
            
            if len(current_words) < self.chunk_overlap or len(next_words) < self.chunk_overlap:
                continue
            
            current_end = current_words[-self.chunk_overlap:]
            next_start = next_words[:self.chunk_overlap]
            
            if current_end != next_start:
                return False
        
        return True
