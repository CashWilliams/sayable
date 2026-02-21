import json
import math
import re

DEFAULT_TRAINING = [
    ("ugh", "groan"),
    ("this is annoying", "groan"),
    ("this is frustrating", "groan"),
    ("this is bad", "groan"),
    ("this is terrible", "groan"),
    ("oh no", "gasp"),
    ("wow", "gasp"),
    ("gosh", "gasp"),
    ("i did not expect this", "gasp"),
    ("i can't believe this", "gasp"),
    ("cool ai news", "gasp"),
    ("what a surprise", "gasp"),
    ("something interesting happened", "gasp"),
    ("this is something interesting", "gasp"),
    ("ahem", "clear_throat"),
    ("clearing my throat", "clear_throat"),
    ("shh", "shush"),
    ("shush", "shush"),
    ("sorry about that", "sigh"),
    ("i guess", "sigh"),
    ("sorry to say this", "sigh"),
    ("sorry to say this but the command failed", "sigh"),
    ("unfortunately that failed", "sigh"),
    ("cough", "cough"),
    ("coughing", "cough"),
    ("sniff", "sniff"),
    ("sniffing", "sniff"),
    ("okay", "none"),
    ("thanks", "none"),
    ("let us continue", "none"),
    ("this is some info", "none"),
    ("this is an update", "none"),
    ("this is a note", "none"),
]

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


class NaiveBayesTagger:
    def __init__(self, model=None):
        self.model = model or train_nb(DEFAULT_TRAINING)

    @classmethod
    def from_json(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            model = json.load(f)
        return cls(model=model)

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
