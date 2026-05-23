## ADDED Requirements

### Requirement: Stable CLI exit codes
The `sayable` CLI SHALL use stable exit codes for expected failure categories.

#### Scenario: Success exits zero
- **WHEN** text is processed successfully
- **THEN** the CLI exits with code `0`

#### Scenario: Bad arguments or bad config exit one
- **WHEN** argparse rejects arguments or config validation fails
- **THEN** the CLI exits with code `1` and prints a concise diagnostic to stderr

#### Scenario: Input read failure exits two
- **WHEN** the configured input file cannot be read
- **THEN** the CLI exits with code `2` and prints the path and error category to stderr

#### Scenario: Output write failure exits three
- **WHEN** the configured output file cannot be written
- **THEN** the CLI exits with code `3` and prints the path and error category to stderr

#### Scenario: Model load failure exits four
- **WHEN** the configured model file cannot be loaded or is malformed
- **THEN** the CLI exits with code `4` and prints a concise diagnostic to stderr

#### Scenario: Unexpected failure exits ninety nine
- **WHEN** an unhandled unexpected error occurs
- **THEN** the CLI exits with code `99` and prints a concise diagnostic to stderr

### Requirement: CLI diagnostics
The `sayable` CLI SHALL keep successful transformed text on stdout and diagnostics on stderr.

#### Scenario: Config error does not pollute stdout
- **WHEN** config validation fails
- **THEN** stdout is empty and stderr contains the diagnostic

#### Scenario: File error does not pollute stdout
- **WHEN** input or output file handling fails
- **THEN** stdout is empty and stderr contains the diagnostic

### Requirement: Install and run smoke paths
The CLI SHALL be smoke-tested through local project execution and installed-script metadata.

#### Scenario: uv run help works
- **WHEN** `uv run sayable --help` is run from the project
- **THEN** help text is printed and the command exits successfully

#### Scenario: stdin pipeline works
- **WHEN** text is piped into `uv run sayable --no-tags`
- **THEN** normalized text is printed to stdout and the command exits successfully

#### Scenario: module execution works
- **WHEN** `python -m sayable --help` is run from an environment with the package importable
- **THEN** CLI help is printed successfully

