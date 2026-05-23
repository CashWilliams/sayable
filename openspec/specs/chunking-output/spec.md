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

