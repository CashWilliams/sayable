import re


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def already_tagged(sentence, allowed_tags):
    for tag in allowed_tags:
        if tag in sentence:
            return True
    return False


def insert_tags(text, classifier, config):
    if not config.get("tagger_enabled", True):
        return text

    allowed_tags = config.get("allowed_tags", [])
    label_to_tag = config.get("label_to_tag", {})
    disabled_tags = set(config.get("disabled_tags", []))
    min_conf = config.get("tag_min_confidence", 0.55)
    position = config.get("tag_position", "prefix")
    strategy = config.get("tagger_strategy", "nb")
    max_tags = config.get("tag_max_per_chunk", 3)

    sentences = split_sentences(text)
    out = []
    inserted = 0

    for sentence in sentences:
        if already_tagged(sentence, allowed_tags):
            out.append(sentence)
            continue

        label, conf = "", 0.0
        lowered = sentence.lower().strip()
        if strategy in {"rules", "rules_nb"}:
            if re.search(r"\bahem\b|clear(?:ing)? my throat", lowered):
                label, conf = "clear_throat", 1.0
            elif re.search(r"\bshh+\b|\bshush\b", lowered):
                label, conf = "shush", 1.0
            elif re.search(r"\bugh+\b", lowered):
                label, conf = "groan", 1.0

        if not label and strategy in {"nb", "rules_nb"}:
            label, conf = classifier.predict(sentence)

        tag = label_to_tag.get(label, "")
        if tag and tag not in disabled_tags and conf >= min_conf and inserted < max_tags:
            inserted += 1
            if position == "suffix":
                out.append(f"{sentence} {tag}")
            else:
                out.append(f"{tag} {sentence}")
        else:
            out.append(sentence)

    return " ".join(out)
