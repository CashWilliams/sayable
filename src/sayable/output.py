from html import escape


def format_output(text, config):
    mode = config.get("output_mode", "plain")
    if mode in {"plain", "chatterbox"}:
        return text
    if mode == "ssml":
        return f"<speak>{escape(text)}</speak>"
    return text

