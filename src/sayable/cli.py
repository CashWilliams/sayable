import argparse
import sys

from .classifier import NaiveBayesTagger
from .chunker import chunk_text
from .config import ConfigError, load_config, validate_config
from .normalizer import normalize_text
from .output import format_output
from .tagger import insert_tags

EXIT_BAD_ARGS_OR_CONFIG = 1
EXIT_INPUT_READ = 2
EXIT_OUTPUT_WRITE = 3
EXIT_MODEL_LOAD = 4
EXIT_UNEXPECTED = 99


class SayableArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(EXIT_BAD_ARGS_OR_CONFIG, f"{self.prog}: error: {message}\n")


def read_input(path):
    if not path or path == "-":
        return sys.stdin.read()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as exc:
        raise OSError(f"input read failed for {path!r}: {exc.strerror or exc}") from exc


def write_output(path, text):
    if not path or path == "-":
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
            if not text.endswith("\n"):
                f.write("\n")
    except OSError as exc:
        raise OSError(f"output write failed for {path!r}: {exc.strerror or exc}") from exc


def build_parser():
    parser = SayableArgumentParser(
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
    parser.add_argument("--chunk-size", type=int, help="Split output into chunks no longer than N characters when possible.")
    parser.add_argument("--chunk-separator", help="Text inserted between chunks.")
    parser.add_argument("--output-mode", choices=["plain", "chatterbox", "ssml"], help="Output format.")
    return parser


def run(args):
    cfg = load_config(args.config)

    if args.no_tags:
        cfg["tagger_enabled"] = False
    if args.time_style:
        cfg["time_style"] = args.time_style
    if args.time_zero:
        cfg["time_zero"] = args.time_zero
    if args.no_am_pm:
        cfg["time_include_am_pm"] = False
    if args.chunk_size is not None:
        cfg["chunk_size"] = args.chunk_size
    if args.chunk_separator is not None:
        cfg["chunk_separator"] = args.chunk_separator
    if args.output_mode:
        cfg["output_mode"] = args.output_mode
    validate_config(cfg)

    try:
        classifier = NaiveBayesTagger.from_json(args.model) if args.model else NaiveBayesTagger()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise RuntimeError(f"model load failed for {args.model!r}: {exc}") from exc

    text = read_input(args.input)
    text = normalize_text(text, cfg)
    text = insert_tags(text, classifier, cfg)
    chunks = chunk_text(text, cfg)
    text = cfg.get("chunk_separator", "\n\n").join(chunks)
    text = format_output(text, cfg)
    write_output(args.output, text)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run(args)
    except ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return EXIT_BAD_ARGS_OR_CONFIG
    except OSError as exc:
        message = str(exc)
        if message.startswith("input read failed"):
            print(message, file=sys.stderr)
            return EXIT_INPUT_READ
        if message.startswith("output write failed"):
            print(message, file=sys.stderr)
            return EXIT_OUTPUT_WRITE
        print(f"file error: {message}", file=sys.stderr)
        return EXIT_INPUT_READ
    except RuntimeError as exc:
        if str(exc).startswith("model load failed"):
            print(str(exc), file=sys.stderr)
            return EXIT_MODEL_LOAD
        print(f"unexpected error: {exc}", file=sys.stderr)
        return EXIT_UNEXPECTED
    except Exception as exc:
        print(f"unexpected error: {exc}", file=sys.stderr)
        return EXIT_UNEXPECTED
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
