from pathlib import Path
from pypdf import PdfReader
from bs4 import BeautifulSoup
import argparse

def load_text(path: Path) -> str:
    """Loads a document into plain text based on its extension."""
    s = path.suffix.lower()
    
    if s == ".pdf":
        text_parts = []
        try:
            reader = PdfReader(path)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_parts.append(extracted)
        except Exception as e:
            raise ValueError(f"Failed to read PDF: {e}")
        return "\n".join(text_parts)
        
    if s in (".txt", ".md"):
        return path.read_text(encoding="utf-8", errors="ignore")
        
    if s in (".html", ".htm"):
        html_content = path.read_text(encoding="utf-8", errors="ignore")
        return BeautifulSoup(html_content, "html.parser").get_text(" ")
        
    raise ValueError(f"unsupported: {s}")

def load_corpus(corpus_dir: str):
    """Loads all documents in a directory and handles errors gracefully."""
    base_path = Path(corpus_dir)
    if not base_path.exists() or not base_path.is_dir():
        print(f"Error: Directory '{corpus_dir}' does not exist.")
        return

    docs = []
    # Using iterdir to find files. Assuming flat directory or simple structure.
    for path in base_path.rglob("*"):
        if not path.is_file():
            continue
            
        try:
            text = load_text(path)
            docs.append({"source": path.name, "text": text})
            # Print success sample
            print(f"OK {path.name}: {len(text)} chars | {text[:60]!r}...")
        except Exception as e:
            # Handle bad files gracefully
            print(f"SKIP {path.name}: {e}")
            
    print(f"\nTotal documents successfully loaded: {len(docs)}")
    return docs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Format Document Loader")
    parser.add_argument("--corpus", default="../data/sample_docs", help="Path to corpus directory")
    args = parser.parse_args()
    
    # Resolve relative path based on script location
    script_dir = Path(__file__).parent
    corpus_path = (script_dir / args.corpus).resolve()
    
    load_corpus(str(corpus_path))
