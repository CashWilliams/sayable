import re


SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text):
    parts = SENTENCE_RE.split(text.strip())
    return [part.strip() for part in parts if part.strip()]


def chunk_text(text, config):
    size = int(config.get("chunk_size", 0) or 0)
    if size <= 0 or len(text) <= size:
        return [text]

    chunks = []
    current = ""

    for paragraph in re.split(r"\n\s*\n", text):
        sentences = split_sentences(paragraph) or [paragraph.strip()]
        for sentence in sentences:
            if not sentence:
                continue
            candidate = f"{current} {sentence}".strip() if current else sentence
            if len(candidate) <= size:
                current = candidate
                continue
            if current:
                chunks.append(current)
                current = ""
            if len(sentence) <= size:
                current = sentence
                continue
            chunks.extend(split_long_sentence(sentence, size))

    if current:
        chunks.append(current)
    return chunks


def split_long_sentence(sentence, size):
    chunks = []
    current = ""
    for token in sentence.split():
        candidate = f"{current} {token}".strip() if current else token
        if len(candidate) <= size:
            current = candidate
            continue
        if current:
            chunks.append(current)
        current = token
    if current:
        chunks.append(current)
    return chunks

