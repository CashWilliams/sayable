## Purpose
Define the `sayable` command-line interface for reading text, applying normalization, optional tag insertion, chunking, output formatting, and writing results.

## Requirements

### Requirement: Command entry point
The package SHALL expose a `sayable` console script that invokes `sayable.cli:main`.

#### Scenario: Project script is declared
- **WHEN** the package metadata is read
- **THEN** `[project.scripts]` contains `sayable = "sayable.cli:main"`

### Requirement: Input and output streams
The CLI SHALL read UTF-8 input from stdin by default or from `--input`, and write UTF-8 output to stdout by default or to `--output`.

#### Scenario: Default input reads stdin
- **WHEN** the CLI is run without `--input`
- **THEN** it reads all text from standard input

#### Scenario: Dash input reads stdin
- **WHEN** `--input -` is provided
- **THEN** it reads all text from standard input

#### Scenario: File input reads UTF-8 file
- **WHEN** `--input path` is provided
- **THEN** it reads the entire UTF-8 file at `path`

#### Scenario: Default output writes stdout
- **WHEN** the CLI is run without `--output`
- **THEN** it writes the result to standard output

#### Scenario: Dash output writes stdout
- **WHEN** `--output -` is provided
- **THEN** it writes the result to standard output

#### Scenario: File output writes UTF-8 file
- **WHEN** `--output path` is provided
- **THEN** it writes the result to the UTF-8 file at `path`

#### Scenario: Output is newline-terminated
- **WHEN** CLI output text does not already end with a newline
- **THEN** the writer appends one newline

### Requirement: Config and model loading
The CLI SHALL load default configuration, optionally overlay a JSON config file, and optionally load a Naive Bayes model from JSON.

#### Scenario: Config file is loaded
- **WHEN** `--config config.json` is provided
- **THEN** the CLI uses `load_config(config.json)`

#### Scenario: Default classifier is used
- **WHEN** `--model` is omitted
- **THEN** the CLI uses a default `NaiveBayesTagger`

#### Scenario: Model file is loaded
- **WHEN** `--model model.json` is provided
- **THEN** the CLI uses `NaiveBayesTagger.from_json(model.json)`

### Requirement: CLI overrides
The CLI SHALL expose targeted flags that override loaded config values for tagging, time handling, chunking, and output mode.

#### Scenario: No-tags disables tag insertion
- **WHEN** `--no-tags` is provided
- **THEN** the CLI sets `tagger_enabled=false`

#### Scenario: Time flags override config
- **WHEN** `--time-style`, `--time-zero`, or `--no-am-pm` are provided
- **THEN** they override `time_style`, `time_zero`, or `time_include_am_pm`

#### Scenario: Chunk flags override config
- **WHEN** `--chunk-size N` or `--chunk-separator TEXT` are provided
- **THEN** they override `chunk_size` or `chunk_separator`

#### Scenario: Output mode flag overrides config
- **WHEN** `--output-mode plain`, `chatterbox`, or `ssml` is provided
- **THEN** it overrides `output_mode`

### Requirement: CLI processing order
The CLI SHALL process text in the order: read input, normalize text, insert tags, chunk text, join chunks, format output, write output.

#### Scenario: Normalization precedes tagging
- **WHEN** input contains patterns handled by normalization and tag-worthy sentences
- **THEN** tag insertion receives normalized text

#### Scenario: Chunking follows tag insertion
- **WHEN** chunking is enabled and tags are inserted
- **THEN** chunk splitting runs after tags have been inserted

#### Scenario: Output formatting is final
- **WHEN** `output_mode="ssml"`
- **THEN** SSML wrapping and XML escaping happen after chunk joining

### Requirement: Help and option validation
The CLI SHALL use argparse to provide help text and validate choices for constrained options.

#### Scenario: Help is available
- **WHEN** `sayable --help` is run
- **THEN** argparse prints a description and the available options

#### Scenario: Time style choices are constrained
- **WHEN** `--time-style` is provided
- **THEN** argparse accepts only `12h` or `24h`

#### Scenario: Time zero choices are constrained
- **WHEN** `--time-zero` is provided
- **THEN** argparse accepts only `oclock` or `hundred`

#### Scenario: Output mode choices are constrained
- **WHEN** `--output-mode` is provided
- **THEN** argparse accepts only `plain`, `chatterbox`, or `ssml`

