## Purpose
Define Sayable's JSON-compatible runtime configuration, default Chatterbox tag set, and override behavior shared by the Python API and CLI.

## Requirements

### Requirement: Default configuration
Sayable SHALL expose a default configuration containing all normalization, tagging, URL, path, markdown, output, and chunking knobs needed by the package. Loading configuration without a path SHALL return an independent copy of those defaults.

#### Scenario: Missing config path uses defaults
- **WHEN** `load_config(None)` is called
- **THEN** the returned config includes the default values such as `time_style="12h"`, `unknown_tag_policy="preserve"`, `tagger_enabled=true`, `output_mode="plain"`, and `chunk_size=0`

#### Scenario: Default config is not shared by reference
- **WHEN** a caller mutates the dictionary returned by `load_config(None)`
- **THEN** later calls to `load_config(None)` SHALL NOT inherit that mutation

### Requirement: JSON config overlay
Sayable SHALL load an optional JSON object from disk and shallow-merge it over the default configuration.

#### Scenario: JSON overrides one field
- **WHEN** a config file contains `{"time_style": "24h"}`
- **THEN** `load_config(path)` returns a config where `time_style` is `24h` and unspecified defaults remain present

#### Scenario: Nested dictionaries are replaced by provided values
- **WHEN** a config file provides an `abbreviations` dictionary
- **THEN** that dictionary SHALL replace the default `abbreviations` value for that loaded config

### Requirement: Supported tag definitions
Sayable SHALL define the default Chatterbox-supported tags as `[clear throat]`, `[sigh]`, `[shush]`, `[cough]`, `[groan]`, `[sniff]`, and `[gasp]`.

#### Scenario: Default allowed tags are available to normalization and tagging
- **WHEN** the default config is loaded
- **THEN** `allowed_tags` contains exactly the supported tag strings and `label_to_tag` maps the supported labels to those tags

#### Scenario: None label maps to no tag
- **WHEN** the tagger predicts the label `none`
- **THEN** `label_to_tag` maps it to an empty string so no paralinguistic tag is inserted

### Requirement: Disabled tags
Sayable SHALL keep `[laugh]` and `[chuckle]` disabled by default so the tagger does not emit them.

#### Scenario: Disabled tags are present in defaults
- **WHEN** the default config is loaded
- **THEN** `disabled_tags` includes `[laugh]` and `[chuckle]`

#### Scenario: Disabled tags do not expand supported tags
- **WHEN** default config is loaded
- **THEN** `[laugh]` and `[chuckle]` SHALL NOT appear in `allowed_tags`

### Requirement: Pronunciation dictionaries
Sayable SHALL provide configurable pronunciation dictionaries for technical terms, domain suffixes, units, acronyms, and abbreviations.

#### Scenario: Technical terms can be pronounced explicitly
- **WHEN** `AI`, `A.I.`, `TTS`, `GPU`, or `CLI` appears in normalized text
- **THEN** the configured technical pronunciation map can convert it to a spoken letter sequence

#### Scenario: Domain suffixes can be pronounced explicitly
- **WHEN** a URL or email domain contains known suffixes such as `com`, `io`, `ai`, or `edu`
- **THEN** the configured domain pronunciation map can provide the spoken form

#### Scenario: Units can be pronounced explicitly
- **WHEN** a supported numeric unit such as `GB`, `GHz`, `ms`, `fps`, `px`, or `%` is normalized
- **THEN** the configured unit pronunciation map can provide the spoken unit name

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

### Requirement: Library transform entry point
Sayable SHALL expose `sayable.transform` as the public pipeline used by the CLI.

#### Scenario: Transform runs the full pipeline
- **WHEN** `transform(text, config=cfg)` is called
- **THEN** it normalizes, optionally tags, chunks, joins chunks, and formats output

#### Scenario: Package exports
- **WHEN** `import sayable` is used
- **THEN** `transform`, `normalize_text`, `load_config`, `ConfigError`, and `__version__` are available
