## ADDED Requirements

### Requirement: Tagger evaluation metrics
Sayable SHALL provide a deterministic way to evaluate tagger quality from labeled data.

#### Scenario: Training can report validation metrics
- **WHEN** the training script is run with validation enabled
- **THEN** it reports label counts, accuracy, and per-label precision or false-positive counts

#### Scenario: Metrics are reproducible
- **WHEN** the same training data, split seed, and training options are used
- **THEN** the reported metrics and model metadata are reproducible

#### Scenario: None-class false positives are visible
- **WHEN** validation examples with label `none` are evaluated
- **THEN** the report includes how often they were incorrectly tagged

### Requirement: Model metadata
Trained tagger model JSON SHALL include metadata sufficient to understand and reproduce the model.

#### Scenario: Model records training metadata
- **WHEN** the training script writes a model
- **THEN** the JSON includes metadata such as schema version, training row count, label counts, smoothing value, source data path or hash, and created timestamp

#### Scenario: Loader accepts current metadata
- **WHEN** `NaiveBayesTagger.from_json(path)` loads a model with metadata
- **THEN** prediction behavior uses the model fields and ignores metadata fields that do not affect inference

### Requirement: False-positive regression coverage
Sayable SHALL maintain tests that protect neutral developer and document text from unnecessary tag insertion.

#### Scenario: Neutral command text is not tagged
- **WHEN** normalized text contains neutral commands such as `uv run pytest`, `git status`, or `curl https://example.com`
- **THEN** the default tagger does not insert paralinguistic tags

#### Scenario: Neutral documentation text is not tagged
- **WHEN** normalized text contains README-style instructions or API documentation without emotional cues
- **THEN** the default tagger does not insert paralinguistic tags

#### Scenario: Disabled tags are never emitted
- **WHEN** classifier output or model data contains a label mapped to a disabled tag
- **THEN** `insert_tags` never emits that disabled tag

### Requirement: Explicit conservative defaults
Sayable SHALL keep the default tagger conservative enough for production pipelines.

#### Scenario: Default minimum confidence is documented and tested
- **WHEN** default config is loaded
- **THEN** `tag_min_confidence` is high enough to avoid common false positives in regression fixtures

#### Scenario: Tag insertion limit applies across mixed strategies
- **WHEN** `tagger_strategy="rules_nb"` and multiple sentences qualify through rules and classifier predictions
- **THEN** `tag_max_per_chunk` limits the combined number of inserted tags

