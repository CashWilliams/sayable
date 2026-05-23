## Context

Sayable is a dependency-light Python package and CLI that rewrites AI-generated, developer-heavy, and document text before it reaches a TTS engine. The current codebase is compact and mostly deterministic, with a small Naive Bayes tagger and JSON config overlay.

The production-readiness gaps are cross-cutting. Configuration is permissive, chunking is character-budget focused rather than span-aware, SSML output is minimal, markdown cleanup is basic, tagger quality is not measured, and CLI failures rely mostly on default exceptions. The design keeps the package lightweight while making these behaviors explicit, testable, and failure-friendly.

## Goals / Non-Goals

**Goals:**
- Add a validation layer that catches bad config before text processing starts.
- Preserve user intent across normalization and chunking, especially around tags, URLs, code, paths, versions, and numeric literals.
- Make output modes predictable for plain text, Chatterbox tags, and SSML consumers.
- Make tagger quality measurable and conservative through metrics, model metadata, and false-positive tests.
- Make CLI errors stable enough for scripts and automation.
- Establish CI, packaging, and regression checks required before calling the package production-ready.

**Non-Goals:**
- Do not turn Sayable into a TTS server, audio renderer, voice UI, or full text-normalization framework.
- Do not add heavyweight grammar, phonemizer, ML, or NLP dependencies to the default path.
- Do not replace the simple public API with a mandatory object model.
- Do not guarantee perfect linguistic normalization for every locale or domain.

## Decisions

### Decision: Centralize config validation in `config.py`

Add a `validate_config(config)` function and a package-specific `ConfigError`. `load_config()` should validate after merging defaults and user JSON. CLI overrides should be applied and then validated again before processing.

Rationale: config errors should be caught once at system boundaries, not as scattered defensive checks inside every normalizer function. This keeps the API predictable and makes CLI failures easy to map to exit codes.

Alternative considered: silently coerce invalid values. That preserves permissiveness but hides production misconfiguration and makes tests less meaningful.

### Decision: Use protected-span tokenization for chunking

Chunking should first identify spans that must not be split, including bracketed tags, URLs, emails, paths, versions, IPs, decimals, phone numbers, markdown inline code, and fenced code/code summaries. Chunking can still split around those spans and can exceed the target size for an individual protected span.

Rationale: TTS chunking is only useful if it does not corrupt syntax that normalization deliberately preserved or created. A small regex-backed span scanner matches the project’s current dependency-light approach.

Alternative considered: parse full markdown/URLs/code into an AST. That is more complete but adds complexity and dependencies out of proportion to this package.

### Decision: Keep SSML output conservative

SSML mode should escape plain text, wrap in `<speak>`, convert configured break markers to `<break>`, and handle Chatterbox tags through a configurable policy: remove, speak, or comment-like placeholder text. Unsupported tags should be escaped as text unless explicitly removed.

Rationale: SSML engines differ in supported expressive tags. Conservative conversion avoids producing invalid or engine-specific SSML while still making the mode useful.

Alternative considered: map each Chatterbox tag to vendor-specific SSML. That would make the default path engine-specific, which conflicts with Sayable’s positioning.

### Decision: Treat tagger quality as release data

Training should produce deterministic model metadata, validation metrics, and label counts. Tests should include false-positive fixtures that protect common neutral developer/document text from unnecessary tags.

Rationale: the tagger’s main production risk is over-insertion. Small measurable gates are more useful here than a bigger model.

Alternative considered: remove ML tagging from production defaults. That would reduce risk but would also remove one of the package’s differentiating features.

### Decision: Make CLI failures scriptable

Define stable non-zero exit codes for bad arguments/config, input/output file errors, model/training data errors, and unexpected failures. Keep normal successful output on stdout and diagnostic errors on stderr.

Rationale: CLI users should be able to use Sayable in shell pipelines without parsing Python tracebacks for expected failures.

Alternative considered: let exceptions propagate. That is simpler but not production-grade for a command-line tool.

## Risks / Trade-offs

- Config validation can reject previously accepted invalid configs -> Mitigation: document accepted values, keep defaults compatible, and make errors actionable.
- Protected chunking can return chunks larger than the target when a protected span is oversized -> Mitigation: explicitly spec this behavior and test it.
- SSML tag policy may not satisfy every engine -> Mitigation: keep output valid and configurable rather than vendor-specific.
- Tagger metrics may be noisy on a small dataset -> Mitigation: use metrics as conservative release gates and expand negative examples first.
- More tests and CI can slow iteration -> Mitigation: keep checks focused on this small package and avoid heavyweight dependencies.

## Migration Plan

1. Add validation primitives and CLI error mapping behind existing defaults.
2. Expand tests around current behavior before changing chunking/output/tagger logic.
3. Implement protected-span chunking and SSML tag policies.
4. Expand tagger training/evaluation output and update the bundled model.
5. Add CI/release checks and README documentation.
6. Archive this change once all tasks pass and specs are synced.
