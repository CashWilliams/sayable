## Why

Sayable has a useful baseline implementation and OpenSpec coverage, but it is not yet production-ready: several behaviors are intentionally minimal, configuration accepts invalid values silently, and quality gates are too thin for a package that rewrites user-authored text before TTS.

This change hardens Sayable into a dependable preprocessing library and CLI by tightening contracts around config validation, protected chunking, output modes, tagger evaluation, CLI failures, and release checks.

## What Changes

- Add explicit configuration validation with actionable errors for unsupported enum values, malformed dictionaries, invalid thresholds, and unsafe chunk/tag limits.
- Make chunking boundary-aware for protected spans such as Chatterbox tags, URLs, emails, paths, versions, IP addresses, decimals, and markdown/code spans.
- Expand output formatting so `ssml` mode has defined behavior for Chatterbox tags and break markers rather than only wrapping escaped text.
- Harden markdown/code cleanup for pasted README, issue, terminal, stack trace, and code-block content with clearer policy behavior.
- Make tagger behavior measurable with validation metrics, false-positive tests, deterministic model metadata, and stronger disabled-tag guarantees.
- Improve CLI production behavior: validation errors, file/model errors, stable exit codes, and smoke-tested install/run paths.
- Add release-quality requirements for CI, coverage-sensitive regression tests, package metadata, and reproducible model training.
- No breaking public API changes are intended; existing simple calls such as `normalize_text(text, config)` and `sayable < input` remain supported.

## Capabilities

### New Capabilities
- `release-quality`: CI, package metadata, regression coverage, reproducible artifacts, and production readiness checks.

### Modified Capabilities
- `configuration`: Add config validation requirements and typed error handling.
- `text-normalization`: Harden markdown/code cleanup and define stronger preservation of user-authored intent.
- `tagging`: Add measurable evaluation, model metadata, false-positive coverage, and stricter disabled-tag behavior.
- `chunking-output`: Add protected-span-aware chunking and richer SSML/tag output behavior.
- `cli`: Add validation/error handling, exit codes, and install/run smoke behavior.

## Impact

- Affected code: `src/sayable/config.py`, `src/sayable/normalizer.py`, `src/sayable/chunker.py`, `src/sayable/output.py`, `src/sayable/tagger.py`, `src/sayable/classifier.py`, `src/sayable/cli.py`, `scripts/train_tag_model.py`.
- Affected tests: broaden unit tests for config, normalization, chunking, output, CLI, training, and false positives.
- Affected data/artifacts: `data/tag_train.csv` and `models/tag_model.json` gain validation/metadata expectations.
- Affected project files: `pyproject.toml`, README usage notes, and CI/release workflow files may be updated.
