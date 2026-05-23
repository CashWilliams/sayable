import re
from html import escape


TAG_RE = re.compile(r"\[[^\]\n]{1,80}\]")


def _break_element(setting):
    if isinstance(setting, str):
        setting = {"time": setting}
    attrs = []
    for key in ("time", "strength"):
        value = setting.get(key)
        if value:
            attrs.append(f'{key}="{escape(value, quote=True)}"')
    return f"<break {' '.join(attrs)}/>"


def _tag_to_words(tag):
    return tag.strip("[]").strip()


def _format_ssml(text, config):
    break_markers = config.get("ssml_break_markers", {})
    tag_policy = config.get("ssml_tag_policy", "remove")

    pieces = []
    pos = 0
    for match in TAG_RE.finditer(text):
        start, end = match.span()
        tag = match.group(0)
        pieces.append(escape(text[pos:start]))
        if tag in break_markers:
            pieces.append(_break_element(break_markers[tag]))
        elif tag_policy == "speak":
            words = _tag_to_words(tag)
            if words:
                pieces.append(escape(words))
        elif tag_policy == "preserve":
            pieces.append(escape(tag))
        pos = end
    pieces.append(escape(text[pos:]))
    body = "".join(pieces)
    body = re.sub(r"\s{2,}", " ", body).strip()
    return f"<speak>{body}</speak>"


def format_output(text, config):
    mode = config.get("output_mode", "plain")
    if mode in {"plain", "chatterbox"}:
        return text
    if mode == "ssml":
        return _format_ssml(text, config)
    return text
