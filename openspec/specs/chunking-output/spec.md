## Purpose
Define Sayable's post-normalization chunk splitting and final output formatting modes.

## Requirements

### Requirement: Chunking disabled by default
Sayable SHALL return the full text as a single chunk when `chunk_size` is absent, zero, negative, or greater than or equal to the text length.

#### Scenario: Default chunking returns one chunk
- **WHEN** `chunk_text(text, config)` is called with default config
- **THEN** it returns a one-item list containing the original text

#### Scenario: Text shorter than size returns one chunk
- **WHEN** `chunk_size` is larger than the input text length
- **THEN** `chunk_text` returns a one-item list containing the original text

### Requirement: Sentence-first chunking
Sayable SHALL split text into chunks at paragraph and sentence boundaries before splitting long sentences by whitespace tokens.

#### Scenario: Sentences fit into target size
- **WHEN** multiple sentences can fit together without exceeding `chunk_size`
- **THEN** they are combined into the same chunk

#### Scenario: Sentence starts a new chunk when candidate is too long
- **WHEN** adding a sentence to the current chunk would exceed `chunk_size`
- **THEN** the current chunk is emitted and the sentence starts a new chunk

#### Scenario: Long sentence is split by tokens
- **WHEN** a single sentence exceeds `chunk_size`
- **THEN** it is split on whitespace tokens into chunks no longer than the target when possible

#### Scenario: Oversized token is preserved
- **WHEN** an individual token is longer than `chunk_size`
- **THEN** that token is emitted as its own chunk rather than being split by characters

### Requirement: Chunk separator
Sayable SHALL join chunks using `chunk_separator` at the CLI pipeline layer after normalization and tag insertion.

#### Scenario: Default separator is blank line
- **WHEN** chunks are joined by the CLI with default config
- **THEN** `\n\n` is inserted between chunks

#### Scenario: Custom separator is supported
- **WHEN** `chunk_separator` is overridden
- **THEN** the CLI joins chunks with the configured separator

### Requirement: Plain and Chatterbox output modes
Sayable SHALL leave text unchanged for `output_mode` values `plain` and `chatterbox`.

#### Scenario: Plain output returns text
- **WHEN** `format_output(text, {"output_mode": "plain"})` is called
- **THEN** it returns `text` unchanged

#### Scenario: Chatterbox output returns text
- **WHEN** `format_output(text, {"output_mode": "chatterbox"})` is called
- **THEN** it returns `text` unchanged, preserving any bracketed tags already present

### Requirement: SSML output mode
Sayable SHALL wrap output in a `<speak>` element and XML-escape text when `output_mode="ssml"`.

#### Scenario: XML-sensitive text is escaped
- **WHEN** `format_output("A < B & C", {"output_mode": "ssml"})` is called
- **THEN** it returns `<speak>A &lt; B &amp; C</speak>`

### Requirement: Unknown output modes
Sayable SHALL return text unchanged for unrecognized output modes.

#### Scenario: Unknown mode is passthrough
- **WHEN** `format_output(text, {"output_mode": "custom"})` is called
- **THEN** it returns `text` unchanged

### Requirement: Protected-span-aware chunking
Sayable SHALL avoid splitting inside protected spans when chunking text.

#### Scenario: Chatterbox tag is not split
- **WHEN** chunking text containing a bracketed tag such as `[clear throat]`
- **THEN** no chunk boundary occurs inside the tag text

#### Scenario: URL and email are not split
- **WHEN** chunking text containing a URL or email address
- **THEN** no chunk boundary occurs inside the URL or email address

#### Scenario: Path and technical scalar are not split
- **WHEN** chunking text containing a file path, version, IP address, decimal, phone number, or currency value
- **THEN** no chunk boundary occurs inside that protected span

#### Scenario: Oversized protected span may exceed target size
- **WHEN** a single protected span is longer than `chunk_size`
- **THEN** the span is emitted intact in one chunk even if that chunk exceeds the target size

### Requirement: Chunking preserves normalized paragraph intent
Sayable SHALL prefer paragraph and sentence boundaries before token boundaries, while preserving protected spans.

#### Scenario: Paragraph boundary is preferred
- **WHEN** text contains paragraph breaks and chunks can remain under target size
- **THEN** chunking prefers paragraph boundaries before sentence or token boundaries

#### Scenario: The CLI pipeline keeps paragraph breaks
- **WHEN** input contains blank-line separated paragraphs and chunking is enabled
- **THEN** normalization and tag insertion preserve those breaks so chunking can use them

#### Scenario: Sentence boundary is preferred
- **WHEN** a paragraph contains multiple sentences and chunks can remain under target size
- **THEN** chunking prefers sentence boundaries before token boundaries

#### Scenario: Token boundary is fallback
- **WHEN** a sentence exceeds target size and has no suitable protected-span boundary
- **THEN** chunking uses whitespace token boundaries as the fallback

### Requirement: SSML tag handling policy
Sayable SHALL define how Chatterbox-style bracket tags are handled when `output_mode="ssml"`.

#### Scenario: Default SSML tag policy removes Chatterbox tags
- **WHEN** SSML output is requested with default tag policy and text contains `[sigh]`
- **THEN** the SSML output does not include raw bracket tags

#### Scenario: SSML speak tag policy verbalizes tags
- **WHEN** SSML output uses a speak-tag policy and text contains `[sigh]`
- **THEN** the tag is converted to safe spoken text inside the `<speak>` document

#### Scenario: Unknown tags are XML-escaped if preserved
- **WHEN** SSML output preserves unknown tags as text
- **THEN** XML-sensitive characters are escaped and the output remains valid XML

### Requirement: SSML break support
Sayable SHALL support configured textual break markers in SSML mode.

#### Scenario: Break marker converts to SSML break
- **WHEN** SSML output is requested and text contains a configured break marker such as `[pause]`
- **THEN** the marker is converted to an SSML `<break>` element with configured duration or strength

#### Scenario: Plain output does not emit SSML break
- **WHEN** plain or Chatterbox output is requested
- **THEN** break markers are handled according to normal tag policy and are not converted to XML elements
