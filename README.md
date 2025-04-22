# Citation Decoder

Citation Decoder is an AI-powered tool that helps researchers understand the citation network within academic papers. It extracts in-text citations from research papers and provides insights about each citation's context, purpose, and relationship to the main paper.

## Features

- **Citation Extraction**: Automatically identifies and extracts in-text citations from PDF research papers
- **Context Analysis**: Analyzes each citation to determine:
  - What the cited paper contributes to the current paper
  - The purpose of the citation (supporting evidence, contrast, background, etc.)
  - Whether the authors agree, critique, or extend the cited work
- **Multiple Input Options**: Upload PDFs directly or provide arXiv links
- **Interactive Interface**: Clean Streamlit UI for easy exploration of citation insights

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/citation-decoder.git
cd citation-decoder

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file and add your API keys
echo "OPENAI_API_KEY=your_openai_api_key" > .env
```

## Usage

```bash
# Run the Streamlit app
streamlit run app.py
```

Then open your browser and navigate to the displayed URL (usually http://localhost:8501).

## Requirements

- Python 3.7+
- PyMuPDF
- OpenAI API key
- Streamlit
- Pandas
- Requests
- python-dotenv

## Project Structure

```
citation-decoder/
├── src/
│   ├── utils/
│   │   ├── pdf_parser.py       # PDF extraction functionality
│   │   ├── citation_analyzer.py # Citation analysis using GPT-4
│   │   └── api_client.py       # API clients for paper metadata
│   └── main.py                 # Core application logic
├── app.py                      # Streamlit web interface
├── requirements.txt            # Project dependencies
└── .env                        # Environment variables (API keys)
```

## Future Improvements

- Citation network visualization
- Integration with more academic paper databases
- Batch processing of multiple papers
- Enhanced pattern matching for more citation styles
- Caching of results for improved performance

## License

MIT

## Acknowledgements

- OpenAI for providing the GPT-4 API
- PyMuPDF for PDF parsing capabilities
- Streamlit for the web application framework
