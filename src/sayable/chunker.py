import re


SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
PROTECTED_PATTERNS = [
    re.compile(r"\[[^\]\n]{1,80}\]"),
    re.compile(r"\b(?:https?://|www\.)[^\s<>]+", re.IGNORECASE),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b[A-Za-z]:\\[^\s)]+"),
    re.compile(r"(?<!\w)(?:~?/)(?:[^\s/]+/)*[^\s/]+"),
    re.compile(r"\bv?\d+(?:\.\d+){1,}\b", re.IGNORECASE),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    re.compile(r"\b\d+\.\d+\b"),
    re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\d)"),
    re.compile(r"(?<!\w)[$€£]\s?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?\b"),
    re.compile(r"`[^`\n]+`"),
]


def split_sentences(text):
    parts = SENTENCE_RE.split(text.strip())
    return [part.strip() for part in parts if part.strip()]


def protected_spans(text):
    spans = []
    for pattern in PROTECTED_PATTERNS:
        spans.extend(match.span() for match in pattern.finditer(text))
    spans.sort()

    merged = []
    for start, end in spans:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def protected_tokens(text):
    spans = protected_spans(text)
    pos = 0
    tokens = []
    for start, end in spans:
        if start > pos:
            tokens.extend(text[pos:start].split())
        tokens.append(text[start:end])
        pos = end
    if pos < len(text):
        tokens.extend(text[pos:].split())
    return tokens


def chunk_text(text, config):
    size = int(config.get("chunk_size", 0) or 0)
    if size <= 0:
        return [text]
    if len(text) <= size and not re.search(r"\n\s*\n", text):
        return [text]

    chunks = []
    current = ""

    def flush():
        nonlocal current
        if current:
            chunks.append(current)
            current = ""

    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) <= size:
            flush()
            chunks.append(paragraph)
            continue

        flush()
        for sentence in split_sentences(paragraph) or [paragraph]:
            if len(sentence) <= size:
                if current and len(current) + 1 + len(sentence) > size:
                    flush()
                current = f"{current} {sentence}".strip() if current else sentence
                continue
            split_long_sentence(sentence, size, chunks)

        flush()

    return chunks


def split_long_sentence(sentence, size, chunks=None):
    own_chunks = chunks is None
    if chunks is None:
        chunks = []

    current = ""
    for token in protected_tokens(sentence):
        candidate = f"{current} {token}".strip() if current else token
        if len(candidate) <= size:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(token) > size:
            chunks.append(token)
            current = ""
        else:
            current = token
    if current:
        chunks.append(current)
    if own_chunks:
        return chunks
    return None
