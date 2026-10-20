import re
from datetime import date

from fpdf import FPDF

_REPLACE = {
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u2022": "-",
    "\u00a0": " ", "\u2192": "->", "\u2264": "<=", "\u2265": ">=",
}


def _clean(text) -> str:
    """Markdown symbols hatao aur PDF-safe text banao."""
    text = str(text)
    text = re.sub(r"\*\*|`", "", text)
    text = re.sub(r"^\s*#+\s*", "", text, flags=re.M)
    for bad, good in _REPLACE.items():
        text = text.replace(bad, good)
    return text.encode("latin-1", "replace").decode("latin-1")


def _marks(q) -> int:
    """marks chahe '2' (string) ho ya 2 (number), dono chalenge."""
    try:
        return int(q.get("marks", 0))
    except (TypeError, ValueError):
        return 0


def _write(pdf: FPDF, text: str, size: int, style: str = "", color=(30, 30, 30), h: int = 6):
    """Safe tarike se text likhta hai (width hamesha poori page width)."""
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", style, size)
    pdf.set_text_color(*color)
    pdf.multi_cell(pdf.epw, h, _clean(text), new_x="LMARGIN", new_y="NEXT")


def build_pdf(subject: str, paper: list[dict], with_answers: bool = False) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    total_marks = sum(_marks(q) for q in paper)
    title = f"{subject} - Answer Key" if with_answers else f"{subject} - Question Paper"

    # ----- Title -----
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(79, 70, 229)
    pdf.multi_cell(pdf.epw, 10, _clean(title), align="C", new_x="LMARGIN", new_y="NEXT")

    _write(pdf, f"Total Marks: {total_marks}   |   Date: {date.today().strftime('%d %b %Y')}",
           10, "", (100, 100, 100), 6)
    pdf.ln(3)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(5)

    # ----- Sections -----
    q_no = 1
    for marks in (1, 2, 4, 8):
        items = [q for q in paper if _marks(q) == marks]
        if not items:
            continue

        _write(pdf, f"Section: {marks} Mark Questions ({len(items)} x {marks} = {len(items) * marks})",
               13, "B", (6, 120, 150), 8)
        pdf.ln(1)

        for q in items:
            _write(pdf, f"Q{q_no}. {q.get('question', '')}  [{marks}]", 11, "B", (30, 30, 30), 6)

            if with_answers:
                _write(pdf, "Answer:", 10, "B", (5, 120, 80), 5)
                _write(pdf, q.get("answer", ""), 10, "", (60, 60, 60), 5)

            pdf.ln(4)
            q_no += 1

    return bytes(pdf.output())