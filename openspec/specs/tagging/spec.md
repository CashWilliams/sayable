## Purpose
Define Sayable's lightweight paralinguistic tag classifier and insertion behavior for Chatterbox Turbo-friendly tags.

## Requirements

### Requirement: Tokenization
The classifier SHALL tokenize lowercase text into alphabetic words with optional apostrophes, numeric tokens, and a small set of emoticon tokens.

#### Scenario: Text tokenizes for training and prediction
- **WHEN** text is passed to the classifier tokenizer
- **THEN** uppercase letters are lowercased and matching word, number, and emoticon tokens are returned

### Requirement: Naive Bayes training
Sayable SHALL provide a multinomial Naive Bayes trainer with additive smoothing and JSON-serializable model output.

#### Scenario: Training creates model fields
- **WHEN** `train_nb(examples)` is called with labeled text examples
- **THEN** the model contains `labels`, `log_priors`, `log_likelihoods`, `vocab`, and `alpha`

#### Scenario: Default classifier trains from bundled examples
- **WHEN** `NaiveBayesTagger()` is constructed without a model
- **THEN** it trains from bundled examples covering supported labels and `none`

#### Scenario: Classifier can load JSON model
- **WHEN** `NaiveBayesTagger.from_json(path)` is called
- **THEN** it loads the model JSON from disk and uses it for prediction

### Requirement: Prediction
The classifier SHALL return the highest-scoring label and a softmax-derived pseudo-confidence.

#### Scenario: Prediction returns label and confidence
- **WHEN** `predict(text)` is called
- **THEN** it returns `(label, confidence)` where confidence is a probability-like float for the selected label

#### Scenario: None remains a valid prediction
- **WHEN** neutral text best matches the `none` class
- **THEN** the classifier may return `none`, causing tag insertion to skip that sentence

### Requirement: Tag insertion controls
Sayable SHALL insert tags only when tagging is enabled, the selected tag is allowed, the tag is not disabled, the confidence meets `tag_min_confidence`, and the per-chunk insertion limit has not been reached.

#### Scenario: Tagging can be disabled
- **WHEN** `tagger_enabled=false`
- **THEN** `insert_tags` returns the input text unchanged

#### Scenario: Confidence threshold gates insertion
- **WHEN** the selected label maps to a tag but confidence is below `tag_min_confidence`
- **THEN** no tag is inserted for that sentence

#### Scenario: Disabled tag gates insertion
- **WHEN** the selected label maps to a disabled tag
- **THEN** no tag is inserted

#### Scenario: Maximum tags per chunk is enforced
- **WHEN** more sentences qualify for tags than `tag_max_per_chunk`
- **THEN** only the first qualifying sentences up to the configured limit receive tags

### Requirement: Sentence-level insertion
Sayable SHALL split input into sentences on punctuation followed by whitespace and consider each sentence independently.

#### Scenario: Already tagged sentence is skipped
- **WHEN** a sentence already contains any configured allowed tag
- **THEN** no additional tag is inserted into that sentence

#### Scenario: Prefix insertion is default
- **WHEN** a sentence qualifies for a tag and `tag_position` is `prefix`
- **THEN** the tag is inserted before the sentence

#### Scenario: Suffix insertion is supported
- **WHEN** a sentence qualifies for a tag and `tag_position` is `suffix`
- **THEN** the tag is inserted after the sentence

### Requirement: Tagger strategies
Sayable SHALL support `tagger_strategy` values that use rules, Naive Bayes, or both.

#### Scenario: Rules strategy detects explicit cues
- **WHEN** `tagger_strategy` is `rules` or `rules_nb`
- **THEN** obvious cues such as `ahem`, `clear my throat`, `shh`, `shush`, and `ugh` map to supported labels with confidence `1.0`

#### Scenario: Naive Bayes strategy predicts from classifier
- **WHEN** `tagger_strategy` is `nb` or `rules_nb` and no rule selected a label
- **THEN** `insert_tags` uses the configured classifier prediction

#### Scenario: Rules-only strategy does not fall back to classifier
- **WHEN** `tagger_strategy` is `rules` and no rule matches
- **THEN** no classifier prediction is used for that sentence

### Requirement: Training script
Sayable SHALL provide a script that trains a tag model from CSV and writes JSON output.

#### Scenario: CSV training data is accepted
- **WHEN** `scripts/train_tag_model.py --data data/tag_train.csv --out models/tag_model.json` is run with CSV columns `text,label`
- **THEN** non-empty rows are trained into a JSON model file

#### Scenario: Empty training data fails
- **WHEN** the training CSV yields no text-label examples
- **THEN** the script exits with an error message instead of writing an empty model

