import pdfplumber


def get_page_count(file) -> int:
    """PDF me total pages kitne hain."""
    file.seek(0)
    with pdfplumber.open(file) as pdf:
        return len(pdf.pages)


def extract_text(file, start_page: int = 1, end_page: int | None = None) -> str:
    """Given page range se text nikalta hai (page numbers 1 se shuru)."""
    file.seek(0)
    texts = []
    with pdfplumber.open(file) as pdf:
        total = len(pdf.pages)
        end_page = min(end_page or total, total)
        for i in range(start_page - 1, end_page):
            page_text = pdf.pages[i].extract_text()
            if page_text:
                texts.append(page_text)
    return "\n\n".join(texts)