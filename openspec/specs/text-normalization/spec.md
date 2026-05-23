## Purpose
Define Sayable's deterministic text normalization behavior for TTS-safe plain text, including markdown cleanup, Chatterbox tag preservation, technical text, dates, numbers, and whitespace.

## Requirements

### Requirement: Line ending and whitespace normalization
Sayable SHALL normalize Windows and classic Mac line endings to `\n`, collapse repeated spaces and tabs, remove spaces before sentence punctuation, and trim the final result.

#### Scenario: Mixed line endings normalize
- **WHEN** input contains `\r\n` or `\r`
- **THEN** normalization treats those line endings as `\n`

#### Scenario: Excess whitespace collapses
- **WHEN** normalized text contains repeated spaces or tabs
- **THEN** the output contains single spaces except where earlier markdown cleanup preserves line boundaries before final whitespace normalization

### Requirement: Markdown cleanup
Sayable SHALL support `markdown_policy` values `plain`, `speak`, and `preserve`. The default `plain` policy SHALL remove markdown syntax while keeping readable text.

#### Scenario: Plain markdown links keep labels
- **WHEN** markdown policy is `plain` and input contains `[docs](https://example.com)`
- **THEN** normalization outputs `docs`

#### Scenario: Speak markdown links include URL text
- **WHEN** markdown policy is `speak` and input contains `[docs](https://example.com)`
- **THEN** normalization includes the label and a spoken form of the URL

#### Scenario: Preserve markdown bypasses markdown cleanup
- **WHEN** markdown policy is `preserve`
- **THEN** markdown cleanup SHALL NOT remove headings, links, code fences, inline backticks, HTML tags, blockquote markers, table separator rows, or shebang lines at that stage

#### Scenario: Inline code removes backticks
- **WHEN** markdown cleanup is active and input contains inline code like `` `uv run pytest` ``
- **THEN** the output contains `uv run pytest`

#### Scenario: Fenced code is controlled by code block policy
- **WHEN** markdown cleanup is active and input contains a fenced code block
- **THEN** `code_block_policy="summarize"` emits `code block omitted`, `strip` removes the block, and `speak` emits `code block` followed by the block body

### Requirement: Explicit sound-effect conversion
Sayable SHALL convert explicit textual sound effects for supported tags into canonical bracket tags before general normalization.

#### Scenario: Supported explicit sound effect is canonicalized
- **WHEN** input contains `(sigh)`, `[gasp]`, or `* cough *`
- **THEN** normalization converts it to the configured canonical supported tag form

#### Scenario: Unsupported explicit sound effect is not emitted as a supported tag
- **WHEN** input contains a sound-effect label not present in `allowed_tags`
- **THEN** explicit sound-effect conversion SHALL NOT create a supported tag for it

### Requirement: Bullet normalization
Sayable SHALL convert simple unordered bullets and numbered bullets into sentence-like text.

#### Scenario: Bullet items become punctuated sentences
- **WHEN** input lines begin with `-`, `*`, `•`, `1.`, or `1)` followed by item text
- **THEN** each item is emitted as text ending in sentence punctuation when missing

### Requirement: Bracketed tag policy
Sayable SHALL protect known tags during normalization and apply `unknown_tag_policy` to unknown bracketed tags. Supported policies are `preserve`, `strip`, and `escape`.

#### Scenario: Known tag is preserved
- **WHEN** input contains `hello [sigh] there`
- **THEN** normalization preserves `[sigh]`

#### Scenario: Unknown tag is preserved by default
- **WHEN** input contains `hello [laugh] there`
- **THEN** default normalization preserves `[laugh]`

#### Scenario: Unknown tag can be stripped
- **WHEN** `unknown_tag_policy="strip"` and input contains `hello [laugh] there`
- **THEN** normalization removes `[laugh]`

#### Scenario: Unknown tag can be escaped
- **WHEN** `unknown_tag_policy="escape"` and input contains `[laugh]`
- **THEN** normalization emits spoken bracket text instead of a bracketed tag

### Requirement: URL, email, path, and social text
Sayable SHALL convert common URL, email, path, handle, hashtag, and Big-O notation into spoken text.

#### Scenario: URL domain policy
- **WHEN** `url_policy="domain"` and input contains `https://example.com/path?q=1`
- **THEN** normalization speaks the domain and omits path, query, and fragment text

#### Scenario: URL full policy
- **WHEN** `url_policy="full"` and input contains URL path segments
- **THEN** normalization speaks path segments separated by `slash`

#### Scenario: URL scheme and port are configurable
- **WHEN** `url_include_scheme=true` or `url_include_port=true`
- **THEN** normalization includes spoken scheme or port information when present

#### Scenario: Email addresses are spoken
- **WHEN** input contains `test.user+ai@example.com`
- **THEN** normalization speaks the local part, `at`, and the domain

#### Scenario: File paths are spoken by default
- **WHEN** input contains a Unix-like path or Windows drive path
- **THEN** normalization speaks path separators, drive names, camel-case boundaries, digits, and punctuation tokens

#### Scenario: Handles and hashtags are spoken
- **WHEN** input contains `@user_name` or `#LaunchDay`
- **THEN** normalization emits `at user name` or `hashtag Launch Day` style text

#### Scenario: Big-O notation is spoken
- **WHEN** input contains `O(n^2)`
- **THEN** normalization emits `big o of n ^ 2` style text

### Requirement: Parentheses, abbreviations, and technical terms
Sayable SHALL apply configured parenthetical handling, abbreviations, technical pronunciation replacements, and acronym spelling.

#### Scenario: Parentheses can expand, unwrap, strip, or preserve
- **WHEN** `paren_policy` is `expand`, `unwrap`, `strip`, or another value
- **THEN** parenthetical text is respectively comma-prefixed, unwrapped, removed, or left unchanged

#### Scenario: Abbreviations expand
- **WHEN** input contains configured abbreviations such as `e.g.`, `i.e.`, `etc.`, `vs.`, `mr.`, `mrs.`, or `dr.`
- **THEN** normalization replaces them with their configured spoken phrase

#### Scenario: Technical terms expand before acronym spelling
- **WHEN** input contains configured technical terms such as `AI`, `A.I.`, `.NET`, `Node.js`, `CI/CD`, `C++`, or `UTF-8`
- **THEN** normalization uses the configured spoken pronunciation

#### Scenario: Acronym spelling is configurable
- **WHEN** `auto_spell_acronyms=true`
- **THEN** two- to six-letter all-caps tokens are lowercased, spelled if forced, or left unchanged if stoplisted

### Requirement: Dates, years, and times
Sayable SHALL convert supported date, year range, ordinal, and time patterns into spoken words.

#### Scenario: ISO date is spoken
- **WHEN** input contains `2026-05-23`
- **THEN** normalization emits `May twenty third twenty twenty six`

#### Scenario: Slash date order is configurable
- **WHEN** input contains `05/23/2026`
- **THEN** `date_order` controls whether the numeric fields are interpreted as `mdy`, `dmy`, or `ymd`

#### Scenario: Month date is spoken
- **WHEN** input contains `May 23, 2026`
- **THEN** normalization emits a spoken month, ordinal day, and year

#### Scenario: Year range is spoken
- **WHEN** input contains `1999-2001`
- **THEN** normalization emits `nineteen ninety nine to two thousand one`

#### Scenario: Time is spoken
- **WHEN** input contains `12:00 pm`
- **THEN** default normalization emits `twelve o'clock p m`

#### Scenario: Time style and zero minute policy are configurable
- **WHEN** `time_style`, `time_zero`, `time_include_am_pm`, or `minute_leading_zero` are changed
- **THEN** time normalization uses those values for supported `HH:MM` patterns

### Requirement: Numeric and technical scalar normalization
Sayable SHALL convert supported numbers, decimals, ordinals, currencies, percentages, fractions, phones, versions, IP addresses, MAC addresses, hex literals, units, slashes, plus signs, ampersands, and minute phrases into spoken words.

#### Scenario: Currency is spoken naturally
- **WHEN** input contains `$12.50`
- **THEN** normalization emits `twelve dollars and fifty cents`

#### Scenario: Percent is spoken
- **WHEN** input contains `42%`
- **THEN** normalization emits `forty two percent`

#### Scenario: Fraction is spoken
- **WHEN** input contains `1/2` or `3/4`
- **THEN** normalization emits `one half` or `three quarters`

#### Scenario: Phone number is spoken in groups by default
- **WHEN** input contains `555-123-4567`
- **THEN** normalization emits digit groups separated by commas

#### Scenario: Version is spoken
- **WHEN** input contains `v1.2.3`
- **THEN** normalization emits `version one point two point three`

#### Scenario: IP address is spoken by digits by default
- **WHEN** input contains `192.168.0.1`
- **THEN** normalization emits each octet as individual digits separated by `dot`

#### Scenario: Units are spoken
- **WHEN** input contains `3.5GHz`, `256GB`, or `2-min`
- **THEN** normalization emits spoken numbers and configured unit names

#### Scenario: Remaining plain numbers are spoken
- **WHEN** supported specialized numeric replacements have run
- **THEN** remaining integer and decimal numeric tokens are converted to words

### Requirement: Emoji stripping
Sayable SHALL strip common emoji ranges and surrogate-codepoint characters when `strip_emoji=true`.

#### Scenario: Emoji are removed by default
- **WHEN** input contains emoji characters
- **THEN** default normalization removes them from the output

#### Scenario: Emoji stripping can be disabled
- **WHEN** `strip_emoji=false`
- **THEN** the emoji stripping stage SHALL NOT remove emoji characters

### Requirement: Pipeline hooks
Sayable SHALL expose `normalize_text(text, config, before=None, after=None)` and `Pipeline(config, before=None, after=None)` hooks that can transform text around named normalization stages.

#### Scenario: Before hooks can run at line endings
- **WHEN** `before` contains a callable for `line_endings`
- **THEN** that callable receives the text and config after line ending normalization

#### Scenario: After hooks can run at named stages
- **WHEN** `after` contains callables keyed by stage names such as `markdown`, `explicit_sfx`, `bullets`, `tag_protection`, `social`, `dates_numbers_units`, `emoji`, or `whitespace`
- **THEN** each matching callable receives the current text and config and its returned text is used for the next stage

#### Scenario: Pipeline delegates to normalize_text
- **WHEN** `Pipeline(config).normalize(text)` is called
- **THEN** it returns the same result as `normalize_text(text, config)` using the configured hooks

