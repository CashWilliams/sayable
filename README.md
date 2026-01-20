# Sayable

Make text sayable for TTS engines (Chatterbox Turbo friendly).

## What it does
- Deterministic text normalization: bullets to sentences, parentheses expansion, emoji stripping, abbreviations.
- Time/number normalization: spell out times, ordinals, decimals, and numeric ranges.
- Tech-aware cleanup: URLs, emails, file paths, versions, IP/MAC/hex, units, and acronyms.
- Lightweight statistical tagger: Naive Bayes inserts supported tags like `[laugh]` or `[sigh]`.

## Install (uv)

```bash
uv tool install sayable
```

Or:

```bash
uv pip install sayable
```

## Quick start

```bash
sayable --help
```

Pipeline usage:

```bash
echo "- wow! 12:00 is late" | sayable
```

## Config
Optional JSON config file:

```json
{
  "time_style": "12h",
  "time_zero": "oclock",
  "time_include_am_pm": true,
  "url_policy": "domain",
  "url_include_scheme": false,
  "paren_policy": "expand",
  "strip_emoji": true,
  "tagger_enabled": true,
  "tag_min_confidence": 0.3
}
```

Run with config:

```bash
sayable --config config.json
```

## Tagging
Supported tags:
`[clear throat]`, `[sigh]`, `[shush]`, `[cough]`, `[groan]`, `[sniff]`, `[gasp]`, `[chuckle]`, `[laugh]`.

The default tagger is intentionally conservative to avoid over-tagging.

## Train your own tagger

```bash
python scripts/train_tag_model.py --data data/tag_train.csv --out models/tag_model.json
```

Then:

```bash
sayable --model models/tag_model.json
```

## Development

```bash
uv run --extra dev pytest
```

Or set up an in-project environment:

```bash
uv sync --extra dev
uv run pytest
```

### Makefile

```bash
make test
```
