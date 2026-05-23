## Purpose
Define release readiness checks for Sayable, including CI, regression coverage, package metadata, documentation, and bundled model reproducibility.

## Requirements

### Requirement: Continuous integration
Sayable SHALL define a CI workflow that runs the production readiness checks on supported Python versions.

#### Scenario: CI runs tests
- **WHEN** CI runs for a pull request or main branch update
- **THEN** it installs development dependencies and runs the test suite

#### Scenario: CI validates OpenSpec
- **WHEN** CI runs for a pull request or main branch update
- **THEN** it runs strict OpenSpec validation for specs and active changes

#### Scenario: CI runs package smoke checks
- **WHEN** CI runs for a pull request or main branch update
- **THEN** it verifies the package can be built or installed and the CLI help path works

### Requirement: Regression test coverage
Sayable SHALL maintain tests covering production-critical behavior across normalization, tagging, chunking, output, config, CLI, and training.

#### Scenario: Normalization regression tests exist
- **WHEN** the test suite runs
- **THEN** it includes representative developer, markdown, documentation, numeric, URL, path, and tag-preservation inputs

#### Scenario: CLI regression tests exist
- **WHEN** the test suite runs
- **THEN** it covers successful stdin/stdout processing and expected failure categories

#### Scenario: Training regression tests exist
- **WHEN** the test suite runs
- **THEN** it covers model training, metadata, validation metrics, and malformed data failures

### Requirement: Package metadata
Sayable SHALL include package metadata sufficient for publishing and installation.

#### Scenario: Project metadata is complete
- **WHEN** package metadata is inspected
- **THEN** it includes name, version, description, readme, Python requirement, license, script entry point, authors or maintainers, and project URLs

#### Scenario: Source distribution includes required artifacts
- **WHEN** the package is built
- **THEN** source distribution or wheel packaging includes source files and required package data while excluding transient test/cache artifacts

### Requirement: Documentation readiness
Sayable SHALL document production-relevant behavior and limits.

#### Scenario: README documents policies
- **WHEN** README usage docs are read
- **THEN** they describe config validation, unknown tag policy, tagger conservatism, chunking limits, output modes, and CLI exit codes

#### Scenario: README documents non-goals
- **WHEN** README docs are read
- **THEN** they state that Sayable is not a TTS server, audio pipeline, universal normalizer, or heavyweight NLP framework

### Requirement: Reproducible bundled model
Sayable SHALL keep the bundled tag model reproducible from checked-in training data.

#### Scenario: Model can be regenerated
- **WHEN** the documented training command is run with the checked-in training data and seed
- **THEN** it can regenerate a model with equivalent inference behavior and metadata

#### Scenario: Model drift is detectable
- **WHEN** the bundled model differs from the checked-in training data or training options
- **THEN** tests or CI detect the drift
