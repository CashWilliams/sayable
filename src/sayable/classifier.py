import json
import math
import re
from importlib.resources import files

TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?|\d+|[:;]-?[)D(]")


def tokenize(text):
    text = text.lower()
    return TOKEN_RE.findall(text)


def train_nb(examples, alpha=1.0):
    labels = sorted({label for _, label in examples})
    label_counts = {label: 0 for label in labels}
    token_counts = {label: {} for label in labels}
    vocab = set()

    for text, label in examples:
        label_counts[label] += 1
        for tok in tokenize(text):
            vocab.add(tok)
            token_counts[label][tok] = token_counts[label].get(tok, 0) + 1

    total_examples = sum(label_counts.values())
    vocab_size = len(vocab)

    log_priors = {}
    log_likelihoods = {label: {} for label in labels}

    for label in labels:
        log_priors[label] = math.log(label_counts[label] / total_examples)
        total_tokens = sum(token_counts[label].values())
        for tok in vocab:
            count = token_counts[label].get(tok, 0)
            prob = (count + alpha) / (total_tokens + alpha * vocab_size)
            log_likelihoods[label][tok] = math.log(prob)

    return {
        "labels": labels,
        "log_priors": log_priors,
        "log_likelihoods": log_likelihoods,
        "vocab": sorted(vocab),
        "alpha": alpha,
    }


def validate_model(model):
    if not isinstance(model, dict):
        raise ValueError("tagger model must be a JSON object")
    for field in ("labels", "log_priors", "log_likelihoods"):
        if field not in model:
            raise ValueError(f"tagger model is missing required field {field!r}")
    labels = model["labels"]
    if not isinstance(labels, list) or not labels or not all(isinstance(label, str) for label in labels):
        raise ValueError("tagger model field 'labels' must be a non-empty list of strings")
    if not isinstance(model["log_priors"], dict) or not isinstance(model["log_likelihoods"], dict):
        raise ValueError("tagger model priors and likelihoods must be objects")
    for label in labels:
        if label not in model["log_priors"] or label not in model["log_likelihoods"]:
            raise ValueError(f"tagger model is missing inference data for label {label!r}")
    return model


def unwrap_model_payload(payload):
    if isinstance(payload, dict) and "model" in payload and isinstance(payload["model"], dict):
        return payload["model"]
    return payload


def load_bundled_model():
    path = files("sayable") / "models" / "tag_model.json"
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return validate_model(unwrap_model_payload(payload))


class NaiveBayesTagger:
    def __init__(self, model=None):
        self.model = validate_model(model) if model is not None else load_bundled_model()

    @classmethod
    def from_json(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            model = json.load(f)
        return cls(model=validate_model(unwrap_model_payload(model)))

    def predict(self, text):
        tokens = tokenize(text)
        labels = self.model["labels"]
        log_priors = self.model["log_priors"]
        log_likelihoods = self.model["log_likelihoods"]

        best_label = "none"
        best_score = float("-inf")

        for label in labels:
            score = log_priors[label]
            ll = log_likelihoods[label]
            for tok in tokens:
                if tok in ll:
                    score += ll[tok]
            if score > best_score:
                best_score = score
                best_label = label

        # Convert to a pseudo-confidence with softmax over labels.
        scores = []
        for label in labels:
            s = log_priors[label]
            ll = log_likelihoods[label]
            for tok in tokens:
                if tok in ll:
                    s += ll[tok]
            scores.append(s)
        max_s = max(scores)
        exps = [math.exp(s - max_s) for s in scores]
        total = sum(exps) or 1.0
        probs = [e / total for e in exps]
        conf = probs[labels.index(best_label)]
        return best_label, conf
