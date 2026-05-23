## ADDED Requirements

### Requirement: Config validation
Sayable SHALL validate merged runtime configuration before text processing uses it.

#### Scenario: Valid default config passes
- **WHEN** `load_config(None)` is called
- **THEN** the returned default configuration passes validation without errors

#### Scenario: Invalid enum value is rejected
- **WHEN** a config contains an unsupported value for an enum-like field such as `time_style`, `time_zero`, `unknown_tag_policy`, `tagger_strategy`, `markdown_policy`, `code_block_policy`, `output_mode`, `date_order`, `year_style`, `currency_style`, `phone_digit_style`, `ip_digit_style`, `url_policy`, `path_policy`, or `tag_position`
- **THEN** validation raises a package-specific config error naming the invalid field and accepted values

#### Scenario: Invalid numeric bound is rejected
- **WHEN** a config contains an invalid numeric value such as negative `tag_min_confidence`, `tag_min_confidence` greater than `1`, negative `tag_max_per_chunk`, or negative `chunk_size`
- **THEN** validation raises a package-specific config error naming the invalid field and accepted range

#### Scenario: Invalid collection type is rejected
- **WHEN** fields such as `allowed_tags`, `disabled_tags`, `acronym_stoplist`, `acronym_force`, `label_to_tag`, `abbreviations`, `tech_pronunciations`, `domain_pronunciations`, or `unit_pronunciations` have the wrong type
- **THEN** validation raises a package-specific config error before normalization begins

### Requirement: CLI overrides are revalidated
Sayable SHALL validate configuration again after CLI flags override loaded config values.

#### Scenario: Config file plus CLI override remains valid
- **WHEN** a valid config file is loaded and valid CLI overrides are applied
- **THEN** the CLI processes input normally

#### Scenario: CLI override cannot create invalid config
- **WHEN** CLI parsing or override application would produce invalid configuration
- **THEN** the CLI exits with the bad-config exit code and prints a concise diagnostic to stderr

### Requirement: Config error type
Sayable SHALL expose a stable package-specific exception type for configuration errors.

#### Scenario: API callers can catch config errors
- **WHEN** invalid config is loaded or validated through the Python API
- **THEN** callers can catch `sayable.config.ConfigError`

