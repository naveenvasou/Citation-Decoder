import fitz  # PyMuPDF
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self, file_path=None, pdf_bytes=None):
        """Initialize with either a file path or PDF bytes"""
        self.file_path = file_path
        self.pdf_bytes = pdf_bytes
        self.doc = None
        self.text = ""
        self.references = []

    def open_pdf(self):
        """Open the PDF document"""
        try:
            if self.file_path:
                self.doc = fitz.open(self.file_path)
            elif self.pdf_bytes:
                self.doc = fitz.open(stream=self.pdf_bytes, filetype="pdf")
            else:
                raise ValueError("Either file_path or pdf_bytes must be provided")
            return True
        except Exception as e:
            logger.error(f"Error opening PDF: {e}")
            return False
        
    def extract_text(self):
        """Extract text from all pages"""
        if not self.doc:
            if not self.open_pdf():
                return False
            
        try:
            self.text=""
            for page in self.doc:
                self.text += page.get_text()

            return True
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return False
        
    def extract_references_section(self):
        """Extract the references section from the paper"""
        if not self.text and not self.extract_text():
            return False
        
        # Common headings for reference sections
        ref_patterns = [
            r"(?:References|Bibliography|Works Cited|Literature Cited)(?:\s|\\n)",
            r"\d+\.\s+(?:References|Bibliography)",
        ]

        # Try to find the references section
        references_text = ""
        for pattern in ref_patterns:
            matches = re.split(pattern, self.text, flags=re.IGNORECASE)
            if len(matches) > 1:
                # Found a references section
                references_text = matches[1]
                
                # Try to find where references end (next section)
                next_section = re.search(r"\n\s*(?:[A-Z][a-z]+\s+)+\n", references_text)
                if next_section:
                    references_text = references_text[:next_section.start()]
                break

        if references_text:
            # Process and clean references
            self.references = self._parse_references(references_text)
            return True
        return False
    
    def _parse_references(self, references_text):
        """Parse individual references from the references section"""
        # Split by patterns like [1], 1., etc.
        refs = re.split(r"\n\s*(?:\[\d+\]|\d+\.)\s+", references_text)
        # Clean up the references
        cleaned_refs = [ref.strip() for ref in refs if ref.strip()]
        return cleaned_refs
    
    def extract_citations(self):
        """Extract in-text citations from the paper"""
        if not self.text and not self.extract_text():
            return []
            
        # Enhanced citation patterns to catch more variations
        citation_patterns = [
            # Author-year patterns
            r'\((?:[A-Za-z\-]+(?:\s+and\s+|\s*,\s*)?)+(?:et\s+al\.)?(?:,\s*\d{4}(?:[a-z])?)+\)',  # (Smith et al., 2019)
            r'\((?:[A-Za-z\-]+(?:\s+and\s+|\s*,\s*)?)+\s+(?:et\s+al\.)\s*(?:,\s*\d{4}(?:[a-z])?)+\)',  # (Smith et al., 2019)
            r'\((?:[A-Za-z\-]+(?:\s+and\s+|\s*,\s*)?)+(?:,\s*\d{4}(?:[a-z])?)+\)',  # (Smith, 2019) or (Smith and Jones, 2019)
            
            # Numeric patterns
            r'\[(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)\]',  # [1] or [1,2,3] or [1-3]
            r'\[(\d+)\]',  # [1]
            r'\((\d+)\)',  # (1)
        ]
        
        citations = []
        seen_positions = set()  # To avoid duplicate citations
        
        for pattern in citation_patterns:
            matches = re.finditer(pattern, self.text)
            for match in matches:
                citation = match.group(0)
                position = (match.start(), match.end())
                
                # Check if we've already seen this position to avoid duplicates
                if position in seen_positions:
                    continue
                    
                seen_positions.add(position)
                
                # Get surrounding context (100 chars before and after)
                start = max(0, match.start() - 100)
                end = min(len(self.text), match.end() + 100)
                context = self.text[start:end]
                
                citations.append({
                    'citation': citation,
                    'context': context,
                    'position': position
                })
        
        return citations
    
    def close(self):
        """Close the PDF document"""
        if self.doc:
            self.doc.close()

    