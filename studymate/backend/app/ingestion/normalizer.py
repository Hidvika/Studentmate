import re
from collections import Counter
from typing import List


class TextNormalizer:
    """Text normalizer for cleaning extracted PDF text."""
    
    def __init__(self) -> None:
        # Common header/footer patterns
        self.header_patterns = [
            r"^\s*\d+\s*$",  # Page numbers
            r"^\s*[A-Z][a-z]+\s+\d+\s*$",  # "Chapter 1" style
            r"^\s*[A-Z\s]+\s*$",  # All caps headers
        ]
        
        # Hyphenation patterns
        self.hyphenation_pattern = re.compile(r"(\w+)-\s*\n\s*(\w+)")
        
        # Multiple whitespace patterns
        self.multiple_newlines = re.compile(r"\n{3,}")
        self.multiple_spaces = re.compile(r" {2,}")
    
    def normalize_text(self, text: str, page_texts: List[str] = None) -> str:
        """Normalize extracted text by applying various cleaning steps."""
        if not text.strip():
            return text
        
        # Step 1: Fix hyphenations
        text = self._fix_hyphenations(text)
        
        # Step 2: Remove repeating headers/footers if page texts provided
        if page_texts:
            text = self._remove_repeating_headers(text, page_texts)
        
        # Step 3: Clean up whitespace
        text = self._clean_whitespace(text)
        
        # Step 4: Fix common OCR issues
        text = self._fix_ocr_issues(text)
        
        return text.strip()
    
    def _fix_hyphenations(self, text: str) -> str:
        """Fix hyphenated words at line breaks."""
        # Fix hyphenations: word-\nword -> wordword
        text = self.hyphenation_pattern.sub(r"\1\2", text)
        
        # Also handle cases with spaces: word- \nword -> wordword
        text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)
        
        return text
    
    def _remove_repeating_headers(self, text: str, page_texts: List[str]) -> str:
        """Remove repeating headers and footers by analyzing page patterns."""
        if not page_texts or len(page_texts) < 3:
            return text
        
        # Find common lines across pages
        page_lines = []
        for page_text in page_texts:
            lines = [line.strip() for line in page_text.split("\n") if line.strip()]
            page_lines.append(lines)
        
        # Find lines that appear in majority of pages
        all_lines = []
        for lines in page_lines:
            all_lines.extend(lines)
        
        line_counts = Counter(all_lines)
        total_pages = len(page_texts)
        threshold = max(2, total_pages // 2)  # Must appear in at least half the pages
        
        # Identify repeating lines
        repeating_lines = {
            line for line, count in line_counts.items() 
            if count >= threshold and self._is_header_footer(line)
        }
        
        if not repeating_lines:
            return text
        
        # Remove repeating lines from text
        lines = text.split("\n")
        filtered_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped not in repeating_lines:
                filtered_lines.append(line)
        
        return "\n".join(filtered_lines)
    
    def _is_header_footer(self, line: str) -> bool:
        """Check if a line looks like a header or footer."""
        line = line.strip()
        
        # Check against patterns
        for pattern in self.header_patterns:
            if re.match(pattern, line):
                return True
        
        # Short lines are likely headers/footers
        if len(line) < 50:
            return True
        
        # Lines with only numbers and common words
        if re.match(r"^[\d\s\-\.]+$", line):
            return True
        
        return False
    
    def _clean_whitespace(self, text: str) -> str:
        """Clean up whitespace issues."""
        # Replace multiple newlines with double newlines
        text = self.multiple_newlines.sub("\n\n", text)
        
        # Replace multiple spaces with single space
        text = self.multiple_spaces.sub(" ", text)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split("\n")]
        
        # Remove empty lines at start and end
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        return "\n".join(lines)
    
    def _fix_ocr_issues(self, text: str) -> str:
        """Fix common OCR issues."""
        # Fix common character substitutions
        replacements = {
            "0": "O",  # Zero to O (context dependent)
            "1": "l",  # One to lowercase L
            "|": "I",  # Pipe to I
            "—": "-",  # Em dash to hyphen
            "–": "-",  # En dash to hyphen
            """: '"',  # Smart quotes to regular quotes
            """: '"',
            "'": "'",  # Smart apostrophe to regular
            "…": "...",  # Ellipsis to three dots
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Fix spacing around punctuation
        text = re.sub(r"\s+([.,;:!?])", r"\1", text)
        text = re.sub(r"([.,;:!?])\s*([A-Z])", r"\1 \2", text)
        
        return text
    
    def handle_two_column_layout(self, text: str) -> str:
        """Attempt to handle two-column layout by reordering text blocks."""
        # This is a simplified approach - in practice, you'd need more sophisticated
        # layout analysis from the PDF extractor
        
        lines = text.split("\n")
        if len(lines) < 10:
            return text
        
        # Simple heuristic: if we have many short lines, it might be two-column
        short_lines = sum(1 for line in lines if len(line.strip()) < 40)
        if short_lines / len(lines) > 0.7:
            # Try to reorder by reading left column first, then right
            # This is a very basic approach
            mid_point = len(lines) // 2
            left_lines = lines[:mid_point]
            right_lines = lines[mid_point:]
            
            # Interleave lines (simplified)
            reordered = []
            max_len = max(len(left_lines), len(right_lines))
            
            for i in range(max_len):
                if i < len(left_lines):
                    reordered.append(left_lines[i])
                if i < len(right_lines):
                    reordered.append(right_lines[i])
            
            return "\n".join(reordered)
        
        return text
