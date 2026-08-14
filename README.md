# Sayable

Make text sayable for TTS engines (Chatterbox Turbo friendly).

## What it does
- Deterministic text normalization: bullets to sentences, parentheses expansion, emoji stripping, abbreviations.
- Time/number normalization: spell out times, ordinals, decimals, and numeric ranges.
- Tech-aware cleanup: URLs, emails, file paths, versions, IP/MAC/hex, units, and acronyms.
- Lightweight statistical tagger: Naive Bayes inserts supported tags like `[gasp]` or `[sigh]`.

## Install (uv)

From GitHub:

```bash
uv tool install git+ssh://git@github.com/CashWilliams/sayable.git
```

HTTPS:

```bash
uv tool install git+https://github.com/CashWilliams/sayable.git
```

Or in a local clone:

```bash
uv tool install -e .
uv tool update-shell
```

## Quick start

```bash
sayable --help
```

Pipeline usage:

```bash
echo "- wow! 12:00 is late" | sayable
```

Python:

```python
from sayable import transform

print(transform("AI at 12:00 pm"))
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
  "tag_min_confidence": 0.55
}
```

Run with config:

```bash
sayable --config config.json
```

Configuration is validated after defaults and JSON config are merged, and again after CLI overrides are applied. Missing config files, invalid JSON, invalid enum values, bad booleans, invalid numeric bounds, and malformed list or dictionary fields raise `sayable.config.ConfigError` in the Python API and exit with code `1` in the CLI.

Production-relevant policies:

- `unknown_tag_policy`: `preserve` keeps unknown bracket tags such as `[laugh]` intact, `strip` removes them, and `escape` verbalizes brackets.
- `markdown_policy`: `plain` removes common markdown syntax, `speak` includes useful link targets, and `preserve` leaves source-like markdown/code available for downstream hooks.
- `code_block_policy`: `summarize` emits short code or stack-trace summaries, `speak` includes code text without fences, and `strip` removes code-like blocks.
- `chunk_size`: `0` disables chunking. Normalization and tagging keep blank-line paragraph breaks, so positive sizes can prefer paragraph and sentence boundaries. Protected spans such as tags, URLs, emails, paths, versions, IPs, decimals, phone numbers, and currency values are not split; a single oversized protected span may exceed the target.
- Versions: `v1.2.3` or three-or-more-component numbers such as `1.2.3` are spoken as versions. Bare decimals such as `3.14` stay decimals.
- `output_mode`: `plain` and `chatterbox` return normalized text, while `ssml` emits a `<speak>` document. In SSML, `ssml_tag_policy` defaults to removing Chatterbox-style tags; `speak` verbalizes them and `preserve` escapes them as text. `ssml_break_markers` maps markers such as `[pause]` to SSML `<break>` elements.

## Tagging
Supported tags:
`[clear throat]`, `[sigh]`, `[shush]`, `[cough]`, `[groan]`, `[sniff]`, `[gasp]`.

Supported utterance labels:
`clear_throat`, `sigh`, `shush`, `cough`, `groan`, `sniff`, `gasp`, `none`.

`none` means "do not insert a tag".

The default tagger is intentionally conservative to avoid over-tagging. The default minimum confidence is chosen to avoid common false positives in neutral command and documentation text, and `tag_max_per_chunk` limits tags across rule and model strategies. Tags listed in `disabled_tags` are never emitted even if model labels map to them.

## CLI exit codes

- `0`: success
- `1`: bad arguments or invalid config
- `2`: input read failure
- `3`: output write failure
- `4`: model load or malformed model failure
- `99`: unexpected failure

Successful transformed text is written to stdout. Diagnostics are written to stderr.

## Train your own tagger

```bash
python scripts/train_tag_model.py --data data/tag_train.csv --out src/sayable/models/tag_model.json --seed 7
```

The training command writes model metadata including schema version, row count, label counts, smoothing value, source data hash, seed, timestamp, and validation metrics. Re-run the documented command against checked-in training data to regenerate the bundled model with equivalent inference behavior.

Then:

```bash
sayable --model src/sayable/models/tag_model.json
```

The default CLI and `transform()` load that bundled model automatically. `--model` is only needed for a custom file. Incomplete model JSON fails at load time with exit code `4`.

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

CI runs the unit suite on supported Python versions, strict OpenSpec validation, package build, wheel install, and CLI smoke checks.

## Non-goals

Sayable is not a TTS server, audio pipeline, universal text normalizer, vendor-specific SSML mapper, or heavyweight NLP framework. It stays dependency-light and focused on preparing text before it reaches a TTS engine.
