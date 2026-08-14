from .classifier import NaiveBayesTagger
from .chunker import chunk_text
from .config import load_config
from .normalizer import normalize_text
from .output import format_output
from .tagger import insert_tags


def transform(text, config=None, model=None):
    cfg = load_config(None) if config is None else config
    classifier = NaiveBayesTagger() if model is None else model
    text = normalize_text(text, cfg)
    text = insert_tags(text, classifier, cfg)
    chunks = chunk_text(text, cfg)
    text = cfg.get("chunk_separator", "\n\n").join(chunks)
    return format_output(text, cfg)
