import re
import unicodedata
from pathlib import Path
from document_loader import load_corpus

def clean(text: str) -> str:
    # fix encoding artifacts
    text = unicodedata.normalize("NFKC", text)
    # normalise line breaks
    text = text.replace("\r\n", "\n")
    # drop footer boilerplate
    text = re.sub(r"Page \d+ of \d+", "", text)
    # drop repeated header boilerplate if any
    text = re.sub(r"COMPANY CONFIDENTIAL", "", text, flags=re.IGNORECASE)
    # collapse spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)
    # collapse blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def run_cleaning_pipeline(corpus_dir: str):
    print("Loading corpus...")
    docs = load_corpus(corpus_dir)
    if not docs:
        print("No docs loaded.")
        return

    print("\nApplying cleaning pipeline...")
    for d in docs:
        before = d["text"]
        after = clean(before)
        d["text"] = after
        
        print(f"\n--- {d['source']} ---")
        print(f"Length: {len(before)} -> {len(after)} chars")
        print("BEFORE:")
        print(repr(before[:150]))
        print("AFTER:")
        print(repr(after[:150]))

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    corpus_path = (script_dir / "../data/sample_docs").resolve()
    run_cleaning_pipeline(str(corpus_path))
