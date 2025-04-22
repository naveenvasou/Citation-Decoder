import logging
from typing import Dict, List, Any, Optional, Union, BinaryIO
import re
import os
from .utils.pdf_parser import PDFParser
from .utils.citation_analyzer import CitationAnalyzer
from .utils.api_client import SemanticScholarClient, ArxivClient
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CitationDecoder:

    def __init__(self):
        """Initialize the CitationDecoder with necessary components"""
        # Load API keys from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        #semantic_scholar_api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

        # Initialize components
        self.citation_analyzer = CitationAnalyzer(api_key=openai_api_key)
        #self.semantic_scholar = SemanticScholarClient(api_key=semantic_scholar_api_key)
        self.arxiv_client = ArxivClient()

    def process_pdf(self, file_path=None, file_bytes=None) -> Dict[str, Any]:
        """
        Process a PDF file to extract and analyze citations
        
        Args:
            file_path: Path to PDF file
            file_bytes: PDF file as bytes
            
        Returns:
            Dictionary with processed data
        """
        # Initialize parser with either file path or bytes
        parser = PDFParser(file_path=file_path, pdf_bytes=file_bytes)
        
        # Extract text and citations
        if not parser.extract_text():
            return {"error": "Failed to extract text from PDF"}
            
        # Extract citations
        citations = parser.extract_citations()
        
        if not citations:
            return {"error": "No citations found in the document"}
            
        # Extract references section
        parser.extract_references_section()
        
        # Clean up
        parser.close()
        
        # Analyze citations
        analyzed_citations = self.citation_analyzer.batch_analyze_citations(citations)
        
        return {
            "citations": analyzed_citations,
            "references": parser.references
        }
    
    def process_arxiv_paper(self, arxiv_id: str) -> Dict[str, Any]:
        """
        Process a paper from arXiv
        
        Args:
            arxiv_id: arXiv ID
            
        Returns:
            Dictionary with processed data
        """
        # Get paper info from arXiv
        paper_info = self.arxiv_client.search_paper(arxiv_id)
        
        if not paper_info:
            return {"error": f"Could not find paper with arXiv ID: {arxiv_id}"}
            
        # Download the PDF
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        try:
            response = requests.get(pdf_url)
            if response.status_code == 200:
                # Process the downloaded PDF
                result = self.process_pdf(file_bytes=response.content)
                
                # Add paper metadata
                result.update({
                    "title": paper_info.get("title"),
                    "authors": paper_info.get("authors"),
                    "abstract": paper_info.get("abstract"),
                    "year": paper_info.get("year")
                })
                
                return result
            else:
                return {"error": f"Failed to download PDF from arXiv: {response.status_code}"}
        except Exception as e:
            return {"error": f"Error processing arXiv paper: {str(e)}"}



    
