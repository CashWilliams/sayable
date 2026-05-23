## ADDED Requirements

### Requirement: Markdown and code policy hardening
Sayable SHALL make markdown and code cleanup deterministic for common pasted README, issue, terminal, and stack trace content.

#### Scenario: Fenced code language marker is not spoken in summarize mode
- **WHEN** markdown cleanup uses `code_block_policy="summarize"` and a fenced code block includes a language marker
- **THEN** the output emits the configured code-block summary without speaking the language marker or code body

#### Scenario: Fenced code speak mode preserves command intent
- **WHEN** markdown cleanup uses `code_block_policy="speak"` and a fenced code block contains shell commands
- **THEN** the output includes spoken code-block text without markdown fence characters

#### Scenario: Stack trace can be summarized or stripped
- **WHEN** input contains a Python-style traceback or common stack trace block
- **THEN** markdown/code cleanup handles it according to the configured code policy rather than reading every frame by default

#### Scenario: Markdown tables do not leak separator syntax
- **WHEN** input contains markdown table header separator rows
- **THEN** normalization removes separator syntax and keeps readable cell text

### Requirement: User-authored intent preservation
Sayable SHALL avoid destructive rewrites of user-authored text unless a config policy explicitly requests them.

#### Scenario: Unknown bracketed engine tag remains intact by default
- **WHEN** input contains an unknown bracketed tag such as `[laugh]`, `[whisper]`, or `[pause]`
- **THEN** default normalization preserves the tag exactly

#### Scenario: Strict tag stripping is explicit
- **WHEN** `unknown_tag_policy="strip"`
- **THEN** only then may unknown bracketed tags be removed

#### Scenario: Markdown preserve mode leaves source-like text intact
- **WHEN** `markdown_policy="preserve"`
- **THEN** markdown and code source syntax remains available for later custom hooks or downstream handling

### Requirement: Normalization regression fixtures
Sayable SHALL maintain regression fixtures for common developer, CLI, documentation, and AI-generated text patterns.

#### Scenario: Developer text fixture remains sayable
- **WHEN** regression tests run against inputs containing commands, paths, URLs, versions, errors, and markdown
- **THEN** normalized output is stable and does not corrupt protected technical tokens

#### Scenario: AI prose fixture remains sayable
- **WHEN** regression tests run against AI-generated prose with bullets, parentheticals, acronyms, and supported tags
- **THEN** normalized output is stable and preserves configured tag behavior

