import openai
import os
import logging
from typing import List, Dict, Any
import google.generativeai as genai


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
genai.configure(api_key="AIzaSyCnHlsIB-xBfouiUJHcA8dYYg4XMAdNOw0")

class CitationAnalyzer:
    def __init__(self, api_key=None):
        """Initialize the CitationAnalyzer with an API key"""
        if api_key:
            openai.api_key = api_key
        else:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            
        if not openai.api_key:
            raise ValueError("OpenAI API key is required. Please provide it or set OPENAI_API_KEY environment variable.")
        self.client = openai.OpenAI(api_key=api_key)  
    
    def analyze_citation(self, citation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single citation with its context
        
        Args:
            citation: Dictionary with citation text and context
            
        Returns:
            Dictionary with analysis results
        """

        try:
            prompt = f"""
            Analyze the following citation in its context:
            
            Citation: {citation['citation']}
            
            Context:
            "{citation['context']}"
            
            Please provide:
            1. What this cited paper contributes to the current paper
            2. The purpose of this citation (e.g., supporting evidence, contrasting view, background information)
            3. The authors' stance towards the cited work (agree, critique, extend, or neutral)
            
            Format your response as a JSON with these keys: "contribution", "purpose", "stance"
            """
            prompt_with_system = """You are a research assistant that analyzes academic citations.""" + prompt
            model = genai.GenerativeModel("models/gemini-1.5-flash-001")
            response = model.generate_content(
            prompt_with_system,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=500,
                ))
        

            # Extract and clean the response
            result = response.text.strip()

            

            # Process the JSON response (in practice, add error handling here)
            import json
            try:
                analysis = json.loads(result)
                citation.update(analysis)
            except json.JSONDecodeError:
                # If response isn't valid JSON, extract info manually
                citation.update({
                    "contribution": "Unable to parse analysis",
                    "purpose": "Unknown",
                    "stance": "Unknown",
                    "raw_analysis": result
                })

            return citation
        
        except Exception as e:
            logger.error(f"Error analyzing citation: {e}")
            citation.update({
                "contribution": f"Error during analysis: {str(e)}",
                "purpose": "Error",
                "stance": "Error"
            })
            return citation
        
    def batch_analyze_citations(self, citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze a batch of citations
        
        Args:
            citations: List of citation dictionaries
            
        Returns:
            List of dictionaries with analysis results
        """

        results = []
        total = len(citations)

        for i, citation in enumerate(citations):
            logger.info(f"Analyzing citation {i+1}/{total}: {citation['citation']}")
            result = self.analyze_citation(citation)
            results.append(result)

        return results