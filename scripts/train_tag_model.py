import argparse
import csv
import json

from sayable.classifier import train_nb


def main():
    parser = argparse.ArgumentParser(description="Train a Naive Bayes tag model.")
    parser.add_argument("--data", required=True, help="CSV with columns: text,label")
    parser.add_argument("--out", required=True, help="Output JSON model file")
    args = parser.parse_args()

    examples = []
    with open(args.data, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = (row.get("text") or "").strip()
            label = (row.get("label") or "").strip()
            if text and label:
                examples.append((text, label))

    if not examples:
        raise SystemExit("No training examples found.")

    model = train_nb(examples)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(model, f, ensure_ascii=True, indent=2)


if __name__ == "__main__":
    main()
