# Review Hardening Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix the correctness, CLI, tagger, pipeline, and packaging issues from the 2026-08-14 codebase review so spoken output, exit codes, and the default model match the documented production behavior.

**Architecture:** Keep Sayable dependency-light. Fix behavior in the existing modules first (normalizer, tagger, classifier, CLI, config, chunker). Then give the CLI and library a single `transform()` composition point. Train and load one bundled Naive Bayes model from package data. Update OpenSpec and tests so the new contracts cannot regress.

**Tech Stack:** Python 3.9+, pytest, uv, setuptools src layout, OpenSpec, stdlib-only runtime.

**TDD:** Every behavior change starts with a failing test. Do not write production code before watching the test fail for the expected reason.

---

## Decisions (locked)

1. **Versions vs decimals.** A token is a version only if it has a `v`/`V` prefix (`v1.2`, `v1.2.3`) or at least three numeric components (`1.2.3`). `3.14` and `3.5` are decimals.
2. **Abbreviation boundaries.** Use real word-character lookarounds `(?<!\w)` / `(?!\w)`.
3. **`date_order="ymd"`.** Accept `YYYY/MM/DD` and two-digit `YY/MM/DD`. Apply the same 70/30 century rule used for other two-digit years.
4. **Tag placeholders.** Use a private-use wrapper that cannot appear in source text: `\ue000sayable:{id}\ue001`. Restore by exact key, longest-first.
5. **12h times.** If the source hour is `>= 12` and no am/pm marker is present, emit `p m`. Hour `0` is `12` a m when no marker is present.
6. **Config errors.** Missing config file, unreadable config file, and invalid JSON are `ConfigError` and CLI exit `1`.
7. **Model load.** `from_json` validates required model fields. Invalid or unreadable models raise a dedicated error that the CLI maps to exit `4`.
8. **Paragraphs.** `normalize_text` and `insert_tags` keep blank-line paragraph breaks. `chunk_text` can then prefer them in the real CLI pipeline.
9. **`markdown_policy="preserve"`.** Skip markdown cleanup and bullet flattening, and keep newlines. Protect fenced code, inline code, and markdown links so later stages do not rewrite them.
10. **Invalid calendar dates.** Leave the original token unchanged (do not speak `thirteen fortieth`).
11. **Emoji flags.** Strip regional-indicator pairs (flags) when `strip_emoji=true`.
12. **Default tagger.** Load the bundled JSON model. Delete the parallel `DEFAULT_TRAINING` list. Train the saved model on **all** labeled rows; compute metrics with a stratified split that never drops a class from the saved model.
13. **Default `tag_min_confidence`.** Raise to `0.55` so the documented conservative default matches the existing false-positive tests.
14. **Public API.** `sayable.transform(text, config=None, model=None)` runs normalize → tag → chunk → join → format. CLI `run()` calls it. Export `transform`, `normalize_text`, `load_config`, `ConfigError`, and `__version__`.
15. **Packaging.** Ship `models/tag_model.json` as package data under `sayable` and load it with `importlib.resources`.
16. **Out of scope.** Do not add a second `currency_style`. Do not split `normalizer.py` in this pass (tests first; split later if the file is still painful). Do not add mypy as a hard CI gate yet; adding Ruff and Python 3.13 to CI is in scope.

---

### Task 1: Versions vs decimals

**Files:**
- Modify: `src/sayable/normalizer.py` (`VERSION_RE`, `replace_versions`)
- Modify: `openspec/specs/text-normalization/spec.md` (version scenario)
- Test: `tests/test_normalizer.py`

**Step 1: Write the failing test**

```python
def test_bare_decimals_are_not_versions(cfg):
    assert normalize_text("The value is 3.14 and also 3.5.", cfg) == (
        "The value is three point one four and also three point five."
    )


def test_dotted_software_versions_still_speak_as_versions(cfg):
    assert normalize_text("Released v1.2.3 and 1.2.3 today.", cfg) == (
        "Released version one point two point three and version one point two point three today."
    )
```

**Step 2: Run test to verify it fails**

Run: `uv run --extra dev pytest tests/test_normalizer.py::test_bare_decimals_are_not_versions tests/test_normalizer.py::test_dotted_software_versions_still_speak_as_versions -v`

Expected: `3.14` currently becomes `version three point fourteen`.

**Step 3: Write minimal implementation**

Change `VERSION_RE` so it matches `v1.2` / `v1.2.3` or `\d+(?:\.\d+){2,}` (three or more components). Keep `v1.2.3 3.5GHz` fixture passing.

**Step 4: Run tests**

Run: `uv run --extra dev pytest tests/test_normalizer.py -v`

Expected: PASS, including `test_units_versions_ip`.

**Step 5: Commit**

```bash
git add tests/test_normalizer.py src/sayable/normalizer.py openspec/specs/text-normalization/spec.md
git commit -m "fix: do not speak bare decimals as software versions"
```

---

### Task 2: Abbreviation word boundaries

**Files:**
- Modify: `src/sayable/normalizer.py` (`replace_abbreviations`)
- Test: `tests/test_normalizer.py`

**Step 1: Write the failing test**

```python
def test_abbreviations_do_not_match_inside_words(cfg):
    cfg["abbreviations"] = {"ok": "okay", "e.g.": "for example"}
    assert normalize_text("booking the room, e.g. now", cfg) == (
        "booking the room, for example now"
    )
```

**Step 2: Run test to verify it fails**

Expected: `booking` becomes `bookaying`.

**Step 3: Write minimal implementation**

```python
pattern = r"(?<!\w)" + re.escape(k) + r"(?!\w)"
```

**Step 4: Run tests and commit**

```bash
git commit -m "fix: honor word boundaries when expanding abbreviations"
```

---

### Task 3: `date_order="ymd"` slash dates

**Files:**
- Modify: `src/sayable/normalizer.py` (`SLASH_DATE_RE`, `replace_dates`)
- Modify: `openspec/specs/text-normalization/spec.md`
- Test: `tests/test_normalizer.py`

**Step 1: Write the failing test**

```python
def test_ymd_slash_dates(cfg):
    cfg["date_order"] = "ymd"
    assert normalize_text("ship on 2026/05/23.", cfg) == (
        "ship on May twenty third twenty twenty six."
    )
    assert normalize_text("ship on 26/05/23.", cfg) == (
        "ship on May twenty third twenty twenty six."
    )
```

**Step 2: Run test to verify it fails**

Expected: `2026/05/23` is not parsed as a date; `26/05/23` is remapped into nonsense.

**Step 3: Write minimal implementation**

- Match both `(\d{4})/(\d{1,2})/(\d{1,2})` and `(\d{1,2})/(\d{1,2})/(\d{2,4})`.
- For `ymd`, interpret four-digit first field as year, otherwise apply the existing 70/30 century rule to the first field.

**Step 4: Run tests and commit**

```bash
git commit -m "fix: interpret ymd slash dates as year-month-day"
```

---

### Task 4: Invalid calendar dates stay literal

**Files:**
- Modify: `src/sayable/normalizer.py` (`date_to_words` / date replacers)
- Test: `tests/test_normalizer.py`

**Step 1: Write the failing test**

```python
def test_impossible_dates_are_left_unchanged(cfg):
    assert "2026-13-40" in normalize_text("On 2026-13-40 we leave.", cfg)
    assert "thirteenth" not in normalize_text("On 2026-13-40 we leave.", cfg).lower()
```

**Step 2: Implement**

If month not in 1–12 or day not in 1–31 (or more precise calendar check), return the original match text.

**Step 3: Commit**

```bash
git commit -m "fix: leave impossible calendar dates unchanged"
```

---

### Task 5: Tag placeholder collision

**Files:**
- Modify: `src/sayable/normalizer.py` (`protect_tags`, `protect_configured_spans`, `restore_tags`)
- Test: `tests/test_normalizer.py`

**Step 1: Write the failing test**

```python
def test_tag_placeholders_do_not_collide_with_source_text(cfg):
    assert normalize_text("keep sayabletaga and [sigh] please", cfg) == (
        "keep sayabletaga and [sigh] please"
    )
```

**Step 2: Implement**

```python
PLACEHOLDER_PREFIX = "\ue000sayable:"
PLACEHOLDER_SUFFIX = "\ue001"
```

Restore longest keys first so prefixes cannot clobber each other.

**Step 3: Commit**

```bash
git commit -m "fix: isolate tag placeholders from source text"
```

---

### Task 6: 12h times infer AM/PM from hour

**Files:**
- Modify: `src/sayable/normalizer.py` (`time_to_words`)
- Test: `tests/test_normalizer.py`

**Step 1: Write the failing test**

```python
def test_24h_clock_values_infer_pm_in_12h_style(cfg):
    assert normalize_text("Meet at 14:00 in the lobby.", cfg) == (
        "Meet at two o'clock p m in the lobby."
    )
    assert normalize_text("Meet at 00:00.", cfg) == "Meet at twelve o'clock a m."
```

Keep the existing `12:00 pm` fixture.

**Step 2: Implement**

When `time_style == "12h"` and `include_am_pm` is true:
- explicit marker wins
- else hour `>= 12` → PM, hour `== 0` → AM
- `12:00` with no marker stays `twelve o'clock` with no suffix (ambiguous noon/midnight only if hour is 12; `00:00` is midnight)

Clarify: `12:00` without marker stays unsuffixed (existing behavior). `00:00` → `twelve o'clock a m`. `14:00` → `two o'clock p m`.

**Step 3: Commit**

```bash
git commit -m "fix: infer am/pm from 24-hour clock values in 12h style"
```

---

### Task 7: Config file errors exit 1

**Files:**
- Modify: `src/sayable/config.py` (`load_config`)
- Modify: `src/sayable/cli.py` if needed
- Test: `tests/test_cli.py`, `tests/test_config.py`

**Step 1: Write the failing tests**

```python
def test_cli_missing_config_file_is_bad_config(capsys):
    assert main(["--config", "/definitely/missing.json"]) == EXIT_BAD_ARGS_OR_CONFIG
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "config error:" in captured.err


def test_cli_malformed_json_config_is_bad_config(tmp_path, capsys, monkeypatch):
    path = tmp_path / "bad.json"
    path.write_text("{nope", encoding="utf-8")
    monkeypatch.setattr("sys.stdin.read", lambda: "hello")
    assert main(["--config", str(path)]) == EXIT_BAD_ARGS_OR_CONFIG
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "config error:" in captured.err
```

**Step 2: Implement**

In `load_config`, wrap `open` `OSError` and `json.JSONDecodeError` as `ConfigError`.

**Step 3: Commit**

```bash
git commit -m "fix: map missing and invalid config files to exit 1"
```

---

### Task 8: Validate tagger models at load time

**Files:**
- Modify: `src/sayable/classifier.py` (`from_json`)
- Modify: `src/sayable/cli.py` (keep mapping to exit 4)
- Test: `tests/test_tagger.py`, `tests/test_cli.py`

**Step 1: Write the failing tests**

A model JSON of `{"foo": 1}` with non-empty stdin must exit `4` with `model load failed` on stderr, not `99`.

Validate presence and types of `labels`, `log_priors`, `log_likelihoods`. Raise `ValueError` (already caught by CLI).

**Step 2: Commit**

```bash
git commit -m "fix: reject malformed tagger models at load time"
```

---

### Task 9: Preserve paragraph breaks through normalize and tag

**Files:**
- Modify: `src/sayable/normalizer.py` (`normalize_bullets`, `normalize_whitespace`)
- Modify: `src/sayable/tagger.py` (`insert_tags`)
- Modify: `src/sayable/chunker.py` if sentence helper is shared
- Test: `tests/test_normalizer.py`, `tests/test_cli.py`

**Step 1: Write the failing tests**

```python
def test_paragraph_breaks_survive_normalization(cfg):
    out = normalize_text("First paragraph.\n\nSecond paragraph.", cfg)
    assert out == "First paragraph.\n\nSecond paragraph."


def test_cli_chunking_prefers_paragraphs(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin.read", lambda: "First paragraph.\n\nSecond paragraph.")
    assert main(["--no-tags", "--chunk-size", "80"]) == 0
    assert capsys.readouterr().out == "First paragraph.\n\nSecond paragraph.\n"
```

`insert_tags` must tag per paragraph and rejoin with `\n\n`.

**Step 2: Implement**

- `normalize_bullets`: blank lines start a new paragraph; join paragraphs with `\n\n`.
- `normalize_whitespace`: collapse spaces/tabs; collapse 3+ newlines to `\n\n`; do not smash `\n\n` into a space.
- `insert_tags`: split on `\n\s*\n`, run the current sentence loop per paragraph, join with `\n\n`.

**Step 3: Commit**

```bash
git commit -m "fix: keep paragraph breaks through normalize, tag, and chunk"
```

---

### Task 10: `markdown_policy="preserve"` keeps source layout

**Files:**
- Modify: `src/sayable/normalizer.py`
- Modify: `openspec/specs/text-normalization/spec.md`
- Test: `tests/test_normalizer.py`

**Step 1: Write the failing test**

```python
def test_markdown_preserve_keeps_source_layout(cfg):
    cfg["markdown_policy"] = "preserve"
    src = "# Title\n\nSee [docs](https://example.com).\n\n```py\nprint(1)\n```"
    assert normalize_text(src, cfg) == src
```

**Step 2: Implement**

When policy is `preserve`:
- skip `normalize_markdown` (already)
- skip `normalize_bullets`
- protect fenced code, inline code, and markdown links in `protect_configured_spans` so URL/number/slash passes do not rewrite them
- keep newlines

**Step 3: Commit**

```bash
git commit -m "fix: leave preserved markdown source intact"
```

---

### Task 11: Strip regional-indicator flag emoji

**Files:**
- Modify: `src/sayable/normalizer.py` (`is_emoji` / `EMOJI_RANGES`)
- Test: `tests/test_normalizer.py`

**Step 1: Write the failing test**

```python
def test_flag_emoji_are_stripped(cfg):
    assert normalize_text("I love the US \U0001f1fa\U0001f1f8 today", cfg) == (
        "I love the US today"
    )
```

**Step 2: Implement**

Treat `0x1F1E6`–`0x1F1FF` as emoji.

**Step 3: Commit**

```bash
git commit -m "fix: strip regional-indicator flag emoji"
```

---

### Task 12: Share sentence splitting and align confidence fallback

**Files:**
- Modify: `src/sayable/chunker.py`, `src/sayable/tagger.py`
- Modify: `src/sayable/config.py` if fallback lives there
- Test: existing tests must stay green; add a unit test that `insert_tags` without `tag_min_confidence` uses `0.55`

**Step 1:** Import `split_sentences` from one module. Change `tagger.py` default `tag_min_confidence` from a magic `0.55` to `config` default (`0.55` after Task 16, keep 0.55 fallback now so this is a no-behavior-change refactor once Task 16 lands). Do this task **after** Task 16 if easier, or set fallback to `0.55` here and change DEFAULT_CONFIG in Task 16.

**Step 2: Commit**

```bash
git commit -m "refactor: share sentence splitting and confidence fallback"
```

---

### Task 13: Raise default `tag_min_confidence` to 0.55

**Files:**
- Modify: `src/sayable/config.py`
- Modify: `tests/test_tagger.py` (stop overriding 0.55)
- Modify: `README.md`, `openspec/specs/tagging/spec.md`

**Step 1: Write / adjust tests**

Neutral command/doc tests must use `load_config(None)` with no confidence override.

Add:

```python
def test_default_confidence_skips_weak_groan(cfg):
    from sayable.classifier import NaiveBayesTagger
    from sayable.tagger import insert_tags
    out = insert_tags("This is interesting.", NaiveBayesTagger(), cfg)
    assert "[groan]" not in out
```

This may only pass after the bundled model + 0.55 default both exist. If it fails on the in-memory trainer before Task 14, keep it in Task 16.

**Step 2: Commit**

```bash
git commit -m "fix: raise default tag confidence to avoid prose false positives"
```

---

### Task 14: Train on all rows and regenerate the bundled model

**Files:**
- Modify: `scripts/train_tag_model.py`
- Modify: `models/tag_model.json` (regenerated)
- Modify: `data/tag_train.csv` only if new `none` examples are needed
- Test: `tests/test_tagger.py`

**Step 1: Write the failing tests**

```python
def test_saved_model_contains_every_training_label(tmp_path):
    # run training script against data/tag_train.csv
    # assert set(model["labels"]) == set(label_counts)
    # assert "clear_throat" in model["labels"]


def test_training_split_does_not_drop_classes_from_saved_model(tmp_path):
    ...
```

**Step 2: Implement**

- Fit `train_nb` on **all** examples for the written `model` payload.
- Compute `metrics` with a stratified holdout or leave-one-out **without** using that reduced set as the saved model.
- If a class has fewer than 2 rows, it still appears in the saved model; metrics may omit it from holdout.

**Step 3: Regenerate**

```bash
uv run python scripts/train_tag_model.py --data data/tag_train.csv --out models/tag_model.json --seed 7
```

Confirm `clear_throat` is in `model.labels`.

**Step 4: Commit**

```bash
git commit -m "fix: train bundled tagger on all labels and regenerate model"
```

---

### Task 15: Load the bundled model by default

**Files:**
- Modify: `src/sayable/classifier.py`
- Modify: `pyproject.toml`, `MANIFEST.in`
- Remove or stop using `DEFAULT_TRAINING`
- Test: `tests/test_tagger.py`

**Step 1: Write the failing test**

```python
def test_default_tagger_uses_bundled_model():
    tagger = NaiveBayesTagger()
    assert "clear_throat" in tagger.model["labels"]
    # bundled model vocab/labels match models/tag_model.json inference fields
```

**Step 2: Implement**

```python
def bundled_model_path():
    return files("sayable") / "models" / "tag_model.json"
```

Copy or move `models/tag_model.json` to `src/sayable/models/tag_model.json` and keep a repo-root `models/tag_model.json` as the training output that is copied into the package (or train `--out` directly into the package path and document that).

Preferred: train writes `models/tag_model.json`; package-data maps that file into the wheel via setuptools package data. If setuptools cannot map an outside file into the package, copy at build time **or** store the canonical file at `src/sayable/models/tag_model.json` and point the README training `--out` there. Pick one canonical path: **`src/sayable/models/tag_model.json`**, update README and the training test, delete the unused root copy **or** keep root as a thin duplicate only if something external depends on it. Prefer one file.

`NaiveBayesTagger()` loads that JSON. `from_json` stays for overrides.

**Step 3: Commit**

```bash
git commit -m "feat: load the bundled tagger model by default"
```

---

### Task 16: Model drift detection

**Files:**
- Test: `tests/test_tagger.py`
- Modify: `.github/workflows/ci.yml` only if a separate step is clearer; a unit test is enough
- Modify: `openspec/specs/release-quality/spec.md` (already requires this)

**Step 1: Write the failing test**

Retrain in a temp file with seed 7 and the checked-in CSV. Compare inference fields (`labels`, `log_priors`, `log_likelihoods`, `vocab`, `alpha`) to the bundled model. Ignore `created_at`.

**Step 2: Commit**

```bash
git commit -m "test: fail CI when the bundled tagger drifts from training data"
```

---

### Task 17: Public `transform()` API

**Files:**
- Create or modify: `src/sayable/__init__.py`, `src/sayable/pipeline.py` (or put `transform` in `cli.py` / a small new module)
- Modify: `src/sayable/cli.py` (`run` calls `transform`)
- Test: `tests/test_cli.py` or `tests/test_api.py`

**Step 1: Write the failing test**

```python
from sayable import transform

def test_transform_matches_cli_pipeline(cfg):
    text = "AI at 12:00 pm"
    assert transform(text, config={**cfg, "tagger_enabled": False}) == (
        "A I at twelve o'clock p m"
    )
```

Also export `__version__` from `importlib.metadata` (fallback to `pyproject` version `0.1.0`).

**Step 2: Implement**

```python
def transform(text, config=None, model=None):
    cfg = config if config is not None else load_config(None)
    classifier = model if model is not None else NaiveBayesTagger()
    text = normalize_text(text, cfg)
    text = insert_tags(text, classifier, cfg)
    chunks = chunk_text(text, cfg)
    text = cfg.get("chunk_separator", "\n\n").join(chunks)
    return format_output(text, cfg)
```

CLI `run()` uses this after loading config/model.

**Step 3: Commit**

```bash
git commit -m "feat: expose sayable.transform as the library pipeline"
```

---

### Task 18: Docs and OpenSpec sync

**Files:**
- `README.md`
- `openspec/specs/text-normalization/spec.md`
- `openspec/specs/cli/spec.md`
- `openspec/specs/tagging/spec.md`
- `openspec/specs/chunking-output/spec.md`
- `openspec/specs/release-quality/spec.md`
- `openspec/specs/configuration/spec.md`

Document: version vs decimal rule, ymd dates, config exit codes, default model load, default confidence 0.55, paragraph preservation, `transform()`, training command path.

**Commit:**

```bash
git commit -m "docs: sync README and OpenSpec with review hardening"
```

---

### Task 19: CI matrix and Ruff

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `pyproject.toml` (optional `[tool.ruff]` + dev extra)
- Modify: `Makefile`

Add Python 3.13 to the test matrix. Add `ruff check src tests` as a CI step. Do not fail on every historic style nit in the first cut — configure Ruff reasonably (`E`, `F`, `I`) and fix what it flags.

**Commit:**

```bash
git commit -m "chore: test Python 3.13 and lint with Ruff"
```

---

## Verification (after all tasks)

```bash
uv run --extra dev pytest
uv run --extra dev pytest tests/test_tagger.py -v
# confirm bundled model labels include clear_throat
python -c "import json; print(json.load(open('src/sayable/models/tag_model.json'))['model']['labels'])"
```

Manual smoke:

```bash
echo "The value is 3.14" | uv run sayable --no-tags
echo "Meet at 14:00" | uv run sayable --no-tags
echo "First.\n\nSecond." | uv run sayable --no-tags --chunk-size 80
```

---

## Execution notes

- Follow TDD for every task. If a new test passes immediately, the test is wrong.
- Do not split `normalizer.py` in this plan.
- Do not add ML dependencies.
- Keep commits scoped to one task.
- After the last task, run the full suite before considering the branch done.
