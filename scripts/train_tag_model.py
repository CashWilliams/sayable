import argparse
import csv
import hashlib
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timezone

from sayable.classifier import NaiveBayesTagger, train_nb


def load_examples(path):
    examples = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or {"text", "label"} - set(reader.fieldnames):
            raise SystemExit("Training data must include text,label columns.")
        for row_number, row in enumerate(reader, start=2):
            text = (row.get("text") or "").strip()
            label = (row.get("label") or "").strip()
            if not text or not label:
                raise SystemExit(f"Missing text or label on row {row_number}.")
            examples.append((text, label))
    if not examples:
        raise SystemExit("No training examples found.")
    return examples


def file_hash(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def split_examples(examples, validation_ratio, seed):
    if validation_ratio <= 0:
        return examples, []
    grouped = defaultdict(list)
    for example in examples:
        grouped[example[1]].append(example)
    rng = random.Random(seed)
    train_examples = []
    validation_examples = []
    for label in sorted(grouped):
        rows = list(grouped[label])
        rng.shuffle(rows)
        if len(rows) < 2:
            train_examples.extend(rows)
            continue
        holdout = max(1, int(round(len(rows) * validation_ratio)))
        holdout = min(holdout, len(rows) - 1)
        validation_examples.extend(rows[:holdout])
        train_examples.extend(rows[holdout:])
    return train_examples, validation_examples


def evaluate(model, examples):
    if not examples:
        return {}
    tagger = NaiveBayesTagger(model)
    total = len(examples)
    correct = 0
    per_label = defaultdict(lambda: {"true": 0, "predicted": 0, "correct": 0})
    none_false_positives = 0
    for text, expected in examples:
        predicted, _confidence = tagger.predict(text)
        per_label[expected]["true"] += 1
        per_label[predicted]["predicted"] += 1
        if predicted == expected:
            correct += 1
            per_label[expected]["correct"] += 1
        if expected == "none" and predicted != "none":
            none_false_positives += 1

    labels = sorted(per_label)
    label_metrics = {}
    for label in labels:
        counts = per_label[label]
        predicted = counts["predicted"] or 1
        label_metrics[label] = {
            "true": counts["true"],
            "predicted": counts["predicted"],
            "correct": counts["correct"],
            "precision": counts["correct"] / predicted,
        }
    return {
        "validation_rows": total,
        "accuracy": correct / total,
        "none_false_positives": none_false_positives,
        "per_label": label_metrics,
    }


def main():
    parser = argparse.ArgumentParser(description="Train a Naive Bayes tag model.")
    parser.add_argument("--data", required=True, help="CSV with columns: text,label")
    parser.add_argument("--out", required=True, help="Output JSON model file")
    parser.add_argument("--seed", type=int, default=7, help="Deterministic validation split seed")
    parser.add_argument("--validation-ratio", type=float, default=0.2, help="Held-out validation ratio")
    parser.add_argument("--alpha", type=float, default=1.0, help="Naive Bayes smoothing value")
    args = parser.parse_args()

    if not 0 <= args.validation_ratio < 1:
        raise SystemExit("--validation-ratio must be >= 0 and < 1.")
    if args.alpha <= 0:
        raise SystemExit("--alpha must be greater than 0.")

    examples = load_examples(args.data)
    train_examples, validation_examples = split_examples(examples, args.validation_ratio, args.seed)
    metrics = evaluate(train_nb(train_examples, alpha=args.alpha), validation_examples)
    model = train_nb(examples, alpha=args.alpha)
    label_counts = dict(sorted(Counter(label for _text, label in examples).items()))
    payload = {
        "metadata": {
            "schema_version": 1,
            "training_rows": len(examples),
            "label_counts": label_counts,
            "smoothing": args.alpha,
            "source_data_path": args.data,
            "source_data_sha256": file_hash(args.data),
            "seed": args.seed,
            "validation_ratio": args.validation_ratio,
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        },
        "metrics": metrics,
        "model": model,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2, sort_keys=True)
        f.write("\n")

    print(json.dumps({"label_counts": label_counts, "metrics": metrics}, sort_keys=True))


if __name__ == "__main__":
    main()
