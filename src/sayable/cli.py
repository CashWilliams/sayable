import argparse
import sys

from .classifier import NaiveBayesTagger
from .config import load_config
from .normalizer import normalize_text
from .tagger import insert_tags


def read_input(path):
    if not path or path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_output(path, text):
    if not path or path == "-":
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
        if not text.endswith("\n"):
            f.write("\n")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Clean text and optionally inject Chatterbox Turbo tags.",
    )
    parser.add_argument("-i", "--input", default="-", help="Input file or '-' for stdin.")
    parser.add_argument("-o", "--output", default="-", help="Output file or '-' for stdout.")
    parser.add_argument("--config", help="Path to JSON config.")
    parser.add_argument("--model", help="Path to JSON tagger model.")
    parser.add_argument("--no-tags", action="store_true", help="Disable tag injection.")
    parser.add_argument("--time-style", choices=["12h", "24h"], help="Override time style.")
    parser.add_argument("--time-zero", choices=["oclock", "hundred"], help="Override time zero policy.")
    parser.add_argument("--no-am-pm", action="store_true", help="Do not include am/pm in 12h style.")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    cfg = load_config(args.config)

    if args.no_tags:
        cfg["tagger_enabled"] = False
    if args.time_style:
        cfg["time_style"] = args.time_style
    if args.time_zero:
        cfg["time_zero"] = args.time_zero
    if args.no_am_pm:
        cfg["time_include_am_pm"] = False

    if args.model:
        classifier = NaiveBayesTagger.from_json(args.model)
    else:
        classifier = NaiveBayesTagger()

    text = read_input(args.input)
    text = normalize_text(text, cfg)
    text = insert_tags(text, classifier, cfg)
    write_output(args.output, text)


if __name__ == "__main__":
    main()
