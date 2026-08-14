import json
from copy import deepcopy

SUPPORTED_TAGS = [
    "[clear throat]",
    "[sigh]",
    "[shush]",
    "[cough]",
    "[groan]",
    "[sniff]",
    "[gasp]",
]

LABEL_TO_TAG = {
    "clear_throat": "[clear throat]",
    "sigh": "[sigh]",
    "shush": "[shush]",
    "cough": "[cough]",
    "groan": "[groan]",
    "sniff": "[sniff]",
    "gasp": "[gasp]",
    "none": "",
}


class ConfigError(ValueError):
    """Raised when Sayable configuration is invalid."""

DEFAULT_CONFIG = {
    "time_style": "12h",
    "time_zero": "oclock",
    "time_include_am_pm": True,
    "minute_leading_zero": "oh",
    "paren_policy": "expand",
    "strip_emoji": True,
    "tagger_enabled": True,
    "tag_min_confidence": 0.55,
    "tag_position": "prefix",
    "unknown_tag_policy": "preserve",
    "disabled_tags": ["[laugh]", "[chuckle]"],
    "tagger_strategy": "nb",
    "tag_max_per_chunk": 3,
    "url_policy": "domain",
    "url_include_scheme": False,
    "url_read_query": False,
    "url_read_fragment": False,
    "url_include_port": True,
    "path_policy": "speak",
    "ip_digit_style": "single",
    "date_order": "mdy",
    "year_style": "auto",
    "currency_style": "natural",
    "phone_digit_style": "grouped",
    "markdown_policy": "plain",
    "code_block_policy": "summarize",
    "output_mode": "plain",
    "ssml_tag_policy": "remove",
    "ssml_break_markers": {"[pause]": {"time": "500ms"}},
    "chunk_size": 0,
    "chunk_separator": "\n\n",
    "auto_spell_acronyms": True,
    "acronym_stoplist": [
        "AM",
        "PM",
        "OK",
        "US",
        "UK",
    ],
    "acronym_force": [
        "AI",
        "ML",
        "NLP",
        "LLM",
        "ASR",
        "TTS",
        "API",
        "SDK",
        "HTTP",
        "HTTPS",
        "URL",
        "URI",
        "DNS",
        "IP",
        "TCP",
        "UDP",
        "SSH",
        "SSL",
        "TLS",
        "JSON",
        "XML",
        "HTML",
        "CSS",
        "JS",
        "TS",
        "SQL",
        "GPU",
        "CPU",
        "RAM",
        "VRAM",
        "SSD",
        "HDD",
        "OS",
        "UI",
        "UX",
        "CLI",
        "IDE",
        "CI",
        "CD",
        "QA",
        "SaaS",
        "PaaS",
        "IaaS",
        "IoT",
        "CUDA",
        "C++",
        "C#",
        "F#",
        "RTX",
        "GPT",
        "UUID",
        "GUID",
        "ASCII",
        "UTF",
        "REST",
        "RGB",
        "BGR",
    ],
    "abbreviations": {
        "e.g.": "for example",
        "i.e.": "that is",
        "etc.": "et cetera",
        "vs.": "versus",
        "mr.": "mister",
        "mrs.": "missus",
        "dr.": "doctor",
    },
    "tech_pronunciations": {
        "AI": "A I",
        "A.I.": "A I",
        "ML": "m l",
        "DL": "d l",
        "LLM": "l l m",
        "NLP": "n l p",
        "ASR": "a s r",
        "TTS": "t t s",
        "API": "a p i",
        "SDK": "s d k",
        "HTTP": "h t t p",
        "HTTPS": "h t t p s",
        "URL": "u r l",
        "URI": "u r i",
        "DNS": "d n s",
        "IP": "i p",
        "TCP": "t c p",
        "UDP": "u d p",
        "SSH": "s s h",
        "SSL": "s s l",
        "TLS": "t l s",
        "JSON": "j s o n",
        "XML": "x m l",
        "HTML": "h t m l",
        "CSS": "c s s",
        "JS": "j s",
        "TS": "t s",
        "SQL": "s q l",
        "GPU": "g p u",
        "CPU": "c p u",
        "RAM": "r a m",
        "VRAM": "v r a m",
        "SSD": "s s d",
        "HDD": "h d d",
        "OS": "o s",
        "UI": "u i",
        "UX": "u x",
        "CLI": "c l i",
        "IDE": "i d e",
        "CI": "c i",
        "CD": "c d",
        "CI/CD": "c i slash c d",
        "QA": "q a",
        "SaaS": "s a a s",
        "PaaS": "p a a s",
        "IaaS": "i a a s",
        "IoT": "i o t",
        "CUDA": "koo da",
        "RTX": "r t x",
        "GPT": "g p t",
        "C++": "c plus plus",
        "C#": "c sharp",
        "F#": "f sharp",
        ".NET": "dot net",
        "Node.js": "node j s",
        "Next.js": "next j s",
        "React.js": "react j s",
        "Vue.js": "vue j s",
        "TypeScript": "type script",
        "JavaScript": "java script",
        "K8s": "k eight s",
        "K3s": "k three s",
        "OAuth": "o auth",
        "JWT": "j w t",
        "gRPC": "g r p c",
        "openmontage": "open mahn tahzh",
        "Open Montage": "open mahn tahzh",
        "UTF-8": "u t f eight",
        "UTF8": "u t f eight",
        "ASCII": "a s c i i",
    },
    "domain_pronunciations": {
        "com": "com",
        "net": "net",
        "org": "org",
        "io": "i o",
        "ai": "A I",
        "dev": "dev",
        "app": "app",
        "edu": "e d u",
        "gov": "gov",
        "co": "co",
        "us": "u s",
        "uk": "u k",
        "gg": "g g",
        "tv": "t v",
        "me": "me",
        "ly": "l y",
    },
    "unit_pronunciations": {
        "kb": "kilobytes",
        "mb": "megabytes",
        "gb": "gigabytes",
        "tb": "terabytes",
        "kib": "kibibytes",
        "mib": "mebibytes",
        "gib": "gibibytes",
        "tib": "tebibytes",
        "hz": "hertz",
        "khz": "kilohertz",
        "mhz": "megahertz",
        "ghz": "gigahertz",
        "kbps": "kilobits per second",
        "mbps": "megabits per second",
        "gbps": "gigabits per second",
        "ms": "milliseconds",
        "s": "seconds",
        "sec": "seconds",
        "secs": "seconds",
        "min": "minutes",
        "mins": "minutes",
        "hr": "hours",
        "hrs": "hours",
        "fps": "frames per second",
        "dpi": "dots per inch",
        "ppi": "pixels per inch",
        "px": "pixels",
        "%": "percent",
    },
    "allowed_tags": SUPPORTED_TAGS,
    "label_to_tag": LABEL_TO_TAG,
}


ENUM_FIELDS = {
    "time_style": {"12h", "24h"},
    "time_zero": {"oclock", "hundred"},
    "minute_leading_zero": {"oh", "zero"},
    "paren_policy": {"strip", "unwrap", "expand", "preserve"},
    "tag_position": {"prefix", "suffix"},
    "unknown_tag_policy": {"preserve", "strip", "escape"},
    "tagger_strategy": {"rules", "nb", "rules_nb"},
    "url_policy": {"domain", "full", "preserve"},
    "path_policy": {"speak", "preserve", "strip"},
    "ip_digit_style": {"single", "grouped"},
    "date_order": {"mdy", "dmy", "ymd"},
    "year_style": {"auto", "digits", "cardinal"},
    "currency_style": {"natural"},
    "phone_digit_style": {"grouped", "single"},
    "markdown_policy": {"plain", "speak", "preserve"},
    "code_block_policy": {"summarize", "speak", "strip"},
    "output_mode": {"plain", "chatterbox", "ssml"},
    "ssml_tag_policy": {"remove", "speak", "preserve"},
}

BOOL_FIELDS = {
    "time_include_am_pm",
    "strip_emoji",
    "tagger_enabled",
    "url_include_scheme",
    "url_read_query",
    "url_read_fragment",
    "url_include_port",
    "auto_spell_acronyms",
}

LIST_FIELDS = {"allowed_tags", "disabled_tags", "acronym_stoplist", "acronym_force"}
DICT_FIELDS = {
    "label_to_tag",
    "abbreviations",
    "tech_pronunciations",
    "domain_pronunciations",
    "unit_pronunciations",
    "ssml_break_markers",
}


def _fail(field, message):
    raise ConfigError(f"Invalid config field '{field}': {message}")


def _check_string_list(config, field):
    value = config.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        _fail(field, "expected a list of strings")


def _check_string_dict(config, field):
    value = config.get(field)
    if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
        _fail(field, "expected a dictionary of string keys and string values")


def _check_break_markers(config):
    markers = config.get("ssml_break_markers")
    if not isinstance(markers, dict):
        _fail("ssml_break_markers", "expected a dictionary")
    for marker, setting in markers.items():
        if not isinstance(marker, str):
            _fail("ssml_break_markers", "marker keys must be strings")
        if isinstance(setting, str):
            continue
        if not isinstance(setting, dict):
            _fail("ssml_break_markers", "marker values must be strings or dictionaries")
        if not any(key in setting for key in ("time", "strength")):
            _fail("ssml_break_markers", "marker dictionaries must include time or strength")
        for key, value in setting.items():
            if key not in {"time", "strength"}:
                _fail("ssml_break_markers", f"unsupported marker option {key!r}")
            if not isinstance(value, str):
                _fail("ssml_break_markers", "marker options must be strings")


def validate_config(config):
    if not isinstance(config, dict):
        raise ConfigError("Config must be a dictionary")

    for field, accepted in ENUM_FIELDS.items():
        value = config.get(field)
        if value not in accepted:
            accepted_values = ", ".join(sorted(accepted))
            _fail(field, f"expected one of: {accepted_values}")

    for field in BOOL_FIELDS:
        if not isinstance(config.get(field), bool):
            _fail(field, "expected a boolean")

    for field in LIST_FIELDS:
        _check_string_list(config, field)

    for field in DICT_FIELDS - {"ssml_break_markers"}:
        _check_string_dict(config, field)
    _check_break_markers(config)

    tag_min_confidence = config.get("tag_min_confidence")
    if not isinstance(tag_min_confidence, (int, float)) or isinstance(tag_min_confidence, bool):
        _fail("tag_min_confidence", "expected a number from 0 to 1")
    if not 0 <= tag_min_confidence <= 1:
        _fail("tag_min_confidence", "expected a number from 0 to 1")

    for field in ("tag_max_per_chunk", "chunk_size"):
        value = config.get(field)
        if not isinstance(value, int) or isinstance(value, bool):
            _fail(field, "expected a non-negative integer")
        if value < 0:
            _fail(field, "expected a non-negative integer")

    chunk_separator = config.get("chunk_separator")
    if not isinstance(chunk_separator, str):
        _fail("chunk_separator", "expected a string")

    allowed = set(config.get("allowed_tags", []))
    for tag in config.get("disabled_tags", []):
        if tag in allowed:
            _fail("disabled_tags", f"{tag!r} cannot also be allowed")

    for label, tag in config.get("label_to_tag", {}).items():
        if label != "none" and tag and tag not in allowed:
            _fail("label_to_tag", f"{label!r} maps to unsupported tag {tag!r}")

    return config


def load_config(path):
    if not path:
        return validate_config(deepcopy(DEFAULT_CONFIG))
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except OSError as exc:
        raise ConfigError(f"could not read config file {path!r}: {exc.strerror or exc}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"config file {path!r} is not valid JSON: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ConfigError("Config file must contain a JSON object")
    cfg = deepcopy(DEFAULT_CONFIG)
    cfg.update(data)
    return validate_config(cfg)
