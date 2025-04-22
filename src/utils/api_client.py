import requests
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticScholarClient:
    """Client for fetching paper information from Semantic Scholar API"""
    BASE_URL = "https://api.semanticscholar.org/v1"

    def __init__(self, api_key=None):
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["x-api-key"] = api_key

    def search_paper(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Search for a paper by title or DOI
        
        Args:
            query: Paper title or DOI
            
        Returns:
            Paper data or None if not found
        """

        try:
            # Check if query is a DOI
            if query.startswith("10."):
                endpoint = f"{self.BASE_URL}/paper/{query}"
            else:
                # Assume it's a title
                endpoint = f"{self.BASE_URL}/paper/search"
                params = {"query": query, "limit": 1}
                response = requests.get(endpoint, headers=self.headers, params=params)
                if response.status_code == 200:
                    results = response.json().get("data", [])
                    if results:
                        # Get the first result's ID
                        paper_id = results[0].get("paperId")
                        if paper_id:
                            endpoint = f"{self.BASE_URL}/paper/{paper_id}"
                        else:
                            return None
                    else:
                        return None
                else:
                    logger.error(f"Error searching for paper: {response.status_code} - {response.text}")
                    return None
            # Get paper details
            response = requests.get(endpoint, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error fetching paper: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error in Semantic Scholar API: {e}")
            return None
        
class ArxivClient:
    """Client for fetching paper information from arXiv API"""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    def search_paper(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """
        Get paper information by arXiv ID
        
        Args:
            arxiv_id: arXiv ID (e.g., 2106.12423)
            
        Returns:
            Paper data or None if not found
        """
        try:
            # Clean the ID if it's a URL
            if '/' in arxiv_id:
                arxiv_id = arxiv_id.split('/')[-1]
            if 'arxiv.org' in arxiv_id.lower():
                arxiv_id = arxiv_id.split('/')[-1]
            if '.pdf' in arxiv_id.lower():
                arxiv_id = arxiv_id.replace('.pdf', '')
                
            # Fetch the paper
            params = {"id_list": arxiv_id, "max_results": 1}
            response = requests.get(self.BASE_URL, params=params)
            
            if response.status_code == 200:
                # Parse XML response
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                # Extract paper info
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                entries = root.findall('atom:entry', ns)
                
                if entries:
                    entry = entries[0]
                    title = entry.find('atom:title', ns).text
                    summary = entry.find('atom:summary', ns).text
                    published = entry.find('atom:published', ns).text
                    authors = [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)]
                    
                    return {
                        'title': title,
                        'abstract': summary,
                        'authors': authors,
                        'year': published[:4],
                        'arxiv_id': arxiv_id
                    }
                    
            return None
                
        except Exception as e:
            logger.error(f"Error in arXiv API: {e}")
            return None

    
            

