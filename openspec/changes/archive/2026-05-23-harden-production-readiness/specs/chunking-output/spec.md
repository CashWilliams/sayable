## ADDED Requirements

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

