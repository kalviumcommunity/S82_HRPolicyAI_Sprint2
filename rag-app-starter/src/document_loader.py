from pathlib import Path
import importlib

try:
    PdfReader = importlib.import_module("pypdf").PdfReader
except ImportError:  # pragma: no cover - optional dependency
    try:
        PdfReader = importlib.import_module("PyPDF2").PdfReader
    except ImportError:  # pragma: no cover - optional dependency
        PdfReader = None

try:
    bs4 = importlib.import_module("bs4")
except ImportError:  # pragma: no cover - optional dependency
    bs4 = None


def load_text(path: Path) -> str:
    """
    Load a supported document and return its content as plain text.
    """

    suffix = path.suffix.lower()

    # PDF
    if suffix == ".pdf":
        reader = PdfReader(path)
        pages = []

        for page in reader.pages:
            pages.append(page.extract_text() or "")

        return "\n".join(pages)

    # TXT and Markdown
    
    if suffix in (".txt", ".md"):
        return path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    # HTML
    if suffix in (".html", ".htm"):
        if bs4 is None:
            raise ImportError(
                "BeautifulSoup is required to read HTML files. Install beautifulsoup4."
            )

        html = path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        soup = bs4.BeautifulSoup(html, "html.parser")

        return soup.get_text(
            separator=" ",
            strip=True
        )

    raise ValueError(f"Unsupported file format: {suffix}")


def load_documents(data_dir="data"):
    """
    Load all supported documents from the data directory.

    Returns:
        List of dictionaries containing source and text.
    """

    documents = []


    data_path = Path(data_dir)

    if not data_path.exists():
        print(f"ERROR: Data directory not found: {data_dir}")
        return documents

    for path in data_path.rglob("*"):

        if not path.is_file():
            continue

        try:
            text = load_text(path)

            documents.append({
                "source": path.name,
                "text": text
            })

            sample = " ".join(text[:100].split())

            print(
                f"OK   {path.name} | "
                f"{len(text)} characters | "
                f"Sample: {sample[:100]}"
            )

        except Exception as error:
            print(
                f"SKIP {path.name} | "
                f"Reason: {error}"
            )

    return documents


if __name__ == "__main__":
    documents = load_documents("data")

    print("\n--------------------------------")
    print(f"Successfully loaded: {len(documents)} documents")
    print("--------------------------------")

    for document in documents:
        print(
            f"Source: {document['source']} | "
            f"Length: {len(document['text'])} characters"
        )