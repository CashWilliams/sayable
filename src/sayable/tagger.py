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
    min_conf = config.get("tag_min_confidence", 0.55)
    position = config.get("tag_position", "prefix")

    sentences = split_sentences(text)
    out = []

    for sentence in sentences:
        if already_tagged(sentence, allowed_tags):
            out.append(sentence)
            continue
        label, conf = classifier.predict(sentence)
        tag = label_to_tag.get(label, "")
        if tag and conf >= min_conf:
            if position == "suffix":
                out.append(f"{sentence} {tag}")
            else:
                out.append(f"{tag} {sentence}")
        else:
            out.append(sentence)

    return " ".join(out)
