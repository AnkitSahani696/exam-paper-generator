def split_into_chunks(text: str, max_chars: int = 6000, overlap: int = 300) -> list[str]:
    """
    Text ko chhote chunks me todta hai.
    - max_chars: ek chunk ki max length
    - overlap: pichle chunk ke last ke kuch characters agle me bhi jate hain,
      taaki beech me baat adhoori na kate.
    Paragraph ke boundary par todne ki koshish karta hai.
    """
    text = text.strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        # Agar ek akela paragraph hi bahut bada hai, usse zabardasti todo
        while len(para) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(para[:max_chars])
            para = para[max_chars - overlap:]

        if len(current) + len(para) + 2 <= max_chars:
            current = f"{current}\n\n{para}" if current else para
        else:
            chunks.append(current)
            # overlap: pichle chunk ka last hissa naye chunk ki shuruat me
            tail = current[-overlap:] if overlap else ""
            current = f"{tail}\n\n{para}" if tail else para

    if current:
        chunks.append(current)

    return chunks


def chunk_stats(chunks: list[str]) -> dict:
    """Chunks ki summary (UI me dikhane ke liye)."""
    if not chunks:
        return {"count": 0, "avg": 0, "largest": 0}
    sizes = [len(c) for c in chunks]
    return {
        "count": len(chunks),
        "avg": sum(sizes) // len(sizes),
        "largest": max(sizes),
    }