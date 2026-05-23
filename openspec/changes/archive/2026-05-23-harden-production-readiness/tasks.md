## 1. Configuration Validation

- [x] 1.1 Add `ConfigError` and `validate_config(config)` in `src/sayable/config.py`.
- [x] 1.2 Validate enum-like fields, booleans, numeric bounds, list fields, and dictionary fields.
- [x] 1.3 Call validation from `load_config()` after JSON merge.
- [x] 1.4 Revalidate config in the CLI after command-line overrides are applied.
- [x] 1.5 Add unit tests for valid defaults, invalid enum values, invalid numeric bounds, invalid collection types, and API catchability.

## 2. CLI Hardening

- [x] 2.1 Add package-specific CLI error handling that keeps transformed text on stdout and diagnostics on stderr.
- [x] 2.2 Map expected failures to stable exit codes: success `0`, bad args/config `1`, input read `2`, output write `3`, model load `4`, unexpected `99`.
- [x] 2.3 Add CLI tests for stdin/stdout success, config failure, missing input file, unwritable output path, malformed model, and help.
- [x] 2.4 Verify `uv run sayable --help`, stdin pipeline usage, and `python -m sayable --help` smoke paths.

## 3. Protected Chunking

- [x] 3.1 Implement protected-span detection for bracket tags, URLs, emails, paths, versions, IPs, decimals, phone numbers, and currency values.
- [x] 3.2 Update `chunk_text` to prefer paragraph and sentence boundaries while never splitting protected spans.
- [x] 3.3 Preserve oversized protected spans intact even when they exceed `chunk_size`.
- [x] 3.4 Add tests for protected Chatterbox tags, URLs, emails, paths, versions, IPs, decimals, phones, currency, and oversized spans.

## 4. Output Modes

- [x] 4.1 Add SSML tag handling policy configuration with default behavior that removes Chatterbox tags from SSML output.
- [x] 4.2 Implement SSML speak/preserve behavior for known and unknown bracket tags while keeping XML valid.
- [x] 4.3 Add configurable SSML break marker conversion for markers such as `[pause]`.
- [x] 4.4 Add output tests for plain, chatterbox, SSML escaping, tag policy variants, unknown tags, and break conversion.

## 5. Normalization Hardening

- [x] 5.1 Harden markdown/code cleanup for fenced code language markers, speak/strip/summarize code policies, markdown tables, and source-preserve mode.
- [x] 5.2 Add stack trace handling according to the configured code policy.
- [x] 5.3 Add regression fixtures covering developer commands, paths, URLs, versions, markdown, AI prose, bullets, parentheticals, acronyms, and tag preservation.
- [x] 5.4 Update README documentation for normalization policies and non-goals.

## 6. Tagger Production Quality

- [x] 6.1 Extend `scripts/train_tag_model.py` with deterministic validation split, seed option, and metrics reporting.
- [x] 6.2 Add model metadata: schema version, row count, label counts, smoothing value, data hash or path, seed, and timestamp.
- [x] 6.3 Update `NaiveBayesTagger.from_json()` to tolerate model metadata while preserving inference.
- [x] 6.4 Expand negative training examples and false-positive tests for neutral command and documentation text.
- [x] 6.5 Add tests that disabled tags are never emitted even if model labels map to them.
- [x] 6.6 Regenerate `models/tag_model.json` from checked-in training data using the documented command.

## 7. Release Quality

- [x] 7.1 Add CI workflow that installs dependencies and runs tests on supported Python versions.
- [x] 7.2 Add CI validation for `openspec validate --specs --strict` and active change validation.
- [x] 7.3 Add package build/install smoke checks to CI.
- [x] 7.4 Complete `pyproject.toml` package metadata with authors or maintainers and project URLs.
- [x] 7.5 Ensure package build includes required source/package data and excludes transient artifacts.
- [x] 7.6 Document CLI exit codes, config validation, tagger conservatism, chunking limits, output modes, and model regeneration.

## 8. Final Verification

- [x] 8.1 Run the full unit test suite.
- [x] 8.2 Run CLI smoke commands locally.
- [x] 8.3 Run strict OpenSpec validation for all specs and the active change.
- [x] 8.4 Review the implementation against each production-readiness spec scenario and close any gaps.
