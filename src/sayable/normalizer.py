import re
import unicodedata
from urllib.parse import parse_qsl, unquote, urlparse


BULLET_RE = re.compile(r"^\s*(?:[-*•]|\d+[\.)])\s+(.*)$")
TIME_RE = re.compile(
    r"\b([01]?\d|2[0-3]):([0-5]\d)(?:\s?(a\.?m\.?|p\.?m\.?))?\b",
    re.IGNORECASE,
)
ORDINAL_RE = re.compile(r"\b(\d+)(st|nd|rd|th)\b", re.IGNORECASE)
DECIMAL_RE = re.compile(r"\b\d+\.\d+\b")
NUMBER_RE = re.compile(r"\b\d{1,3}(?:,\d{3})+\b|\b\d+\b")
SFX_RE = re.compile(r"(\*\s*|\(|\[)\s*(sigh|laugh|chuckle|gasp|groan|cough|sniff|shush|clear throat)\s*(\*\s*|\)|\])", re.IGNORECASE)
URL_RE = re.compile(r"\b(?:https?://|www\.)[^\s<>]+", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
HANDLE_RE = re.compile(r"(?<!\w)@([A-Za-z0-9_]{1,30})")
HASHTAG_RE = re.compile(r"(?<!\w)#([A-Za-z0-9_]+)")
WIN_PATH_RE = re.compile(r"\b[A-Za-z]:\\[^\s)]+")
UNIX_PATH_RE = re.compile(r"(?<!\w)(?:~?/)(?:[^\s/]+/)*[^\s/]+")
VERSION_RE = re.compile(r"\bv?(\d+(?:\.\d+)+)\b", re.IGNORECASE)
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
MAC_RE = re.compile(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b")
HEX_RE = re.compile(r"\b0x[0-9A-Fa-f]+\b")
UNIT_RE = re.compile(
    r"\b(\d+(?:\.\d+)?)\s?(kb|mb|gb|tb|kib|mib|gib|tib|hz|khz|mhz|ghz|kbps|mbps|gbps|ms|s|sec|secs|min|mins|hr|hrs|fps|dpi|ppi|px|%)\b",
    re.IGNORECASE,
)
HYPHEN_UNIT_RE = re.compile(
    r"\b(\d+(?:\.\d+)?)-(kb|mb|gb|tb|kib|mib|gib|tib|hz|khz|mhz|ghz|kbps|mbps|gbps|ms|s|sec|secs|min|mins|hr|hrs|fps|dpi|ppi|px|%)\b",
    re.IGNORECASE,
)
QUANT_MIN_RE = re.compile(
    r"\b(a|an|one|two|three|four|five|six|seven|eight|nine|ten|couple|few|several)\s+(min|mins)\b",
    re.IGNORECASE,
)
MINIMUM_RE = re.compile(r"\bthe min\b", re.IGNORECASE)
BIG_O_RE = re.compile(r"\bO\(([^)]+)\)", re.IGNORECASE)

EMOJI_RANGES = [
    (0x1F300, 0x1F5FF),
    (0x1F600, 0x1F64F),
    (0x1F680, 0x1F6FF),
    (0x1F700, 0x1F77F),
    (0x1F780, 0x1F7FF),
    (0x1F800, 0x1F8FF),
    (0x1F900, 0x1F9FF),
    (0x1FA00, 0x1FA6F),
    (0x1FA70, 0x1FAFF),
    (0x2600, 0x26FF),
    (0x2700, 0x27BF),
]


ONES = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
]
TEENS = [
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
]
TENS = [
    "",
    "",
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
]
SCALES = [
    (1_000_000_000, "billion"),
    (1_000_000, "million"),
    (1_000, "thousand"),
    (100, "hundred"),
]


def is_emoji(ch):
    cp = ord(ch)
    if cp == 0xFE0F:
        return True
    for start, end in EMOJI_RANGES:
        if start <= cp <= end:
            return True
    return False


def strip_emoji(text):
    return "".join(ch for ch in text if not is_emoji(ch))


def spell_letters(token):
    return " ".join(ch.lower() for ch in token if ch.isalnum())


def split_camel(token):
    return re.sub(r"([a-z])([A-Z])", r"\1 \2", token)


def digits_to_words(digits):
    return " ".join(ONES[int(ch)] for ch in digits)


def decimal_to_words(num_str):
    whole, frac = num_str.split(".")
    words = number_to_words(int(whole)) + " point "
    words += " ".join(ONES[int(ch)] for ch in frac)
    return words


def speak_token(token):
    token = split_camel(token)
    token = token.replace("-", " dash ").replace("_", " underscore ").replace(".", " dot ")
    token = re.sub(r"\d+", lambda m: number_to_words(int(m.group(0))), token)
    return normalize_whitespace(token)

def number_to_words(n):
    if n < 0:
        return "minus " + number_to_words(-n)
    if n < 10:
        return ONES[n]
    if n < 20:
        return TEENS[n - 10]
    if n < 100:
        tens = TENS[n // 10]
        ones = n % 10
        if ones == 0:
            return tens
        return f"{tens} {ONES[ones]}"

    for scale, name in SCALES:
        if n >= scale:
            if scale == 100:
                lead = number_to_words(n // scale)
                rest = n % scale
                if rest == 0:
                    return f"{lead} {name}"
                return f"{lead} {name} {number_to_words(rest)}"
            lead = number_to_words(n // scale)
            rest = n % scale
            if rest == 0:
                return f"{lead} {name}"
            return f"{lead} {name} {number_to_words(rest)}"
    return str(n)


def ordinal_to_words(n):
    base = number_to_words(n)
    if base.endswith("one"):
        return base[:-3] + "first"
    if base.endswith("two"):
        return base[:-3] + "second"
    if base.endswith("three"):
        return base[:-5] + "third"
    if base.endswith("five"):
        return base[:-4] + "fifth"
    if base.endswith("eight"):
        return base[:-5] + "eighth"
    if base.endswith("nine"):
        return base[:-4] + "ninth"
    if base.endswith("twelve"):
        return base[:-6] + "twelfth"
    if base.endswith("y"):
        return base[:-1] + "ieth"
    return base + "th"


def replace_ordinals(text):
    def repl(match):
        num = int(match.group(1))
        return ordinal_to_words(num)

    return ORDINAL_RE.sub(repl, text)


def replace_decimals(text):
    def repl(match):
        raw = match.group(0)
        whole, frac = raw.split(".")
        words = number_to_words(int(whole)) + " point "
        words += " ".join(ONES[int(ch)] for ch in frac)
        return words

    return DECIMAL_RE.sub(repl, text)


def replace_numbers(text):
    def repl(match):
        raw = match.group(0).replace(",", "")
        try:
            n = int(raw)
        except ValueError:
            return raw
        return number_to_words(n)

    return NUMBER_RE.sub(repl, text)


def replace_big_o(text):
    def repl(match):
        inner = match.group(1).strip()
        inner = split_camel(inner.replace("^", " ^ "))
        inner = inner.replace("/", " slash ")
        return f"big o of {inner}"

    return BIG_O_RE.sub(repl, text)


def replace_versions(text):
    def repl(match):
        raw = match.group(1)
        parts = raw.split(".")
        words = " point ".join(number_to_words(int(p)) for p in parts)
        return f"version {words}"

    return VERSION_RE.sub(repl, text)


def replace_ip_addresses(text, config):
    digit_style = config.get("ip_digit_style", "single")

    def repl(match):
        parts = match.group(0).split(".")
        spoken = []
        for part in parts:
            if digit_style == "single":
                spoken.append(digits_to_words(part))
            else:
                spoken.append(number_to_words(int(part)))
        return " dot ".join(spoken)

    return IP_RE.sub(repl, text)


def replace_mac_addresses(text):
    def repl(match):
        pairs = match.group(0).split(":")
        spoken = []
        for pair in pairs:
            spoken.append(spell_letters(pair))
        return " colon ".join(spoken)

    return MAC_RE.sub(repl, text)


def replace_hex_numbers(text):
    def repl(match):
        raw = match.group(0)[2:]
        return "hex " + spell_letters(raw)

    return HEX_RE.sub(repl, text)


def replace_units(text, config):
    unit_map = config.get("unit_pronunciations", {})

    def repl(match):
        number = match.group(1)
        unit = match.group(2)
        unit_key = unit.lower()
        unit_words = unit_map.get(unit_key, unit_key)
        if "." in number:
            number_words = decimal_to_words(number)
        else:
            number_words = number_to_words(int(number))
        return f"{number_words} {unit_words}"

    return UNIT_RE.sub(repl, text)


def replace_hyphen_units(text):
    return HYPHEN_UNIT_RE.sub(r"\1 \2", text)


def replace_minute_quantifiers(text):
    def repl(match):
        quant = match.group(1).lower()
        if quant in {"a", "an", "one"}:
            return "a minute"
        return f"{quant} minutes"

    return QUANT_MIN_RE.sub(repl, text)


def replace_minimum_phrases(text):
    return MINIMUM_RE.sub("the minimum", text)


def time_to_words(hour, minute, am_pm, config):
    time_style = config.get("time_style", "12h")
    time_zero = config.get("time_zero", "oclock")
    include_am_pm = config.get("time_include_am_pm", True)
    leading_zero = config.get("minute_leading_zero", "oh")

    if time_style == "12h":
        h = hour % 12
        if h == 0:
            h = 12
        hour_words = number_to_words(h)
        if minute == 0:
            if time_zero == "oclock":
                base = f"{hour_words} o'clock"
            else:
                base = f"{hour_words} hundred"
        else:
            if minute < 10:
                minute_words = f"{leading_zero} {ONES[minute]}"
            else:
                minute_words = number_to_words(minute)
            base = f"{hour_words} {minute_words}"
        suffix = ""
        if am_pm and include_am_pm:
            suffix = " a m" if am_pm.startswith("a") else " p m"
        return (base + suffix).strip()

    hour_words = number_to_words(hour)
    if minute == 0:
        if time_zero == "hundred":
            return f"{hour_words} hundred"
        return f"{hour_words} o'clock"
    if minute < 10:
        minute_words = f"{leading_zero} {ONES[minute]}"
    else:
        minute_words = number_to_words(minute)
    return f"{hour_words} {minute_words}"


def replace_times(text, config):
    def repl(match):
        hour = int(match.group(1))
        minute = int(match.group(2))
        am_pm = match.group(3)
        if am_pm:
            am_pm = am_pm.lower().replace(".", "")
        return time_to_words(hour, minute, am_pm, config)

    return TIME_RE.sub(repl, text)


def split_trailing_punct(token):
    trailing = ""
    while token and token[-1] in ".,!?)]}\"'":
        trailing = token[-1] + trailing
        token = token[:-1]
    return token, trailing


def speak_domain_part(part, config):
    domain_map = config.get("domain_pronunciations", {})
    key = part.lower()
    if key in domain_map:
        return domain_map[key]
    if key == "www":
        return spell_letters("www")
    if part.isdigit():
        return number_to_words(int(part))
    if part.isupper() and 2 <= len(part) <= 6:
        return spell_letters(part)
    return speak_token(part)


def speak_domain(host, config):
    parts = [p for p in host.split(".") if p]
    spoken = []
    for idx, part in enumerate(parts):
        if idx > 0:
            spoken.append("dot")
        spoken.append(speak_domain_part(part, config))
    return " ".join(spoken)


def url_to_words(url, config):
    include_scheme = config.get("url_include_scheme", False)
    policy = config.get("url_policy", "domain")
    read_query = config.get("url_read_query", False)
    read_fragment = config.get("url_read_fragment", False)
    include_port = config.get("url_include_port", True)

    original = url
    if url.lower().startswith("www."):
        url = "http://" + url

    parsed = urlparse(url)
    scheme = parsed.scheme
    netloc = parsed.netloc or parsed.path
    path = parsed.path if parsed.netloc else ""

    if "@" in netloc:
        netloc = netloc.split("@", 1)[1]

    port = ""
    if ":" in netloc:
        host, port = netloc.rsplit(":", 1)
    else:
        host = netloc

    host_words = speak_domain(host, config) if host else speak_token(original)
    parts = []
    if include_scheme and scheme:
        parts.append(spell_letters(scheme))
        parts.append("colon")
    parts.append(host_words)

    if include_port and port:
        parts.append("colon")
        parts.append(number_to_words(int(port)))

    if policy == "full":
        if path:
            segments = [s for s in path.split("/") if s]
            for segment in segments:
                parts.append("slash")
                parts.append(speak_token(unquote(segment)))

        if read_query and parsed.query:
            parts.append("question mark")
            q_parts = []
            for key, value in parse_qsl(parsed.query, keep_blank_values=True):
                key_words = speak_token(unquote(key))
                if value:
                    value_words = speak_token(unquote(value))
                    q_parts.append(f"{key_words} equals {value_words}")
                else:
                    q_parts.append(key_words)
            parts.append(" and ".join(q_parts))

        if read_fragment and parsed.fragment:
            parts.append("hash")
            parts.append(speak_token(unquote(parsed.fragment)))

    return normalize_whitespace(" ".join(parts))


def replace_urls(text, config):
    def repl(match):
        url = match.group(0)
        core, trailing = split_trailing_punct(url)
        return url_to_words(core, config) + trailing

    return URL_RE.sub(repl, text)


def replace_emails(text, config):
    def repl(match):
        email = match.group(0)
        local, domain = email.split("@", 1)
        local = split_camel(local)
        local = local.replace(".", " dot ").replace("_", " underscore ").replace("-", " dash ").replace("+", " plus ")
        local = re.sub(r"\d+", lambda m: digits_to_words(m.group(0)), local)
        domain_words = speak_domain(domain, config)
        return normalize_whitespace(f"{local} at {domain_words}")

    return EMAIL_RE.sub(repl, text)


def path_to_words(path, windows=False):
    if windows:
        drive = path[0].upper()
        rest = path[2:].lstrip("\\")
        parts = [p for p in rest.split("\\") if p]
        spoken = [f"{drive} drive"]
        for part in parts:
            spoken.append("slash")
            spoken.append(speak_token(part))
        return " ".join(spoken)

    if path.startswith("~/"):
        spoken = ["home"]
        rest = path[2:]
    elif path.startswith("/"):
        spoken = ["slash"]
        rest = path[1:]
    else:
        spoken = []
        rest = path
    parts = [p for p in rest.split("/") if p]
    for part in parts:
        if spoken and spoken[-1] != "slash":
            spoken.append("slash")
        spoken.append(speak_token(part))
    return " ".join(spoken)


def replace_paths(text, config):
    if not config.get("path_policy", "speak"):
        return text

    def repl_win(match):
        path = match.group(0)
        core, trailing = split_trailing_punct(path)
        return path_to_words(core, windows=True) + trailing

    def repl_unix(match):
        path = match.group(0)
        core, trailing = split_trailing_punct(path)
        return path_to_words(core, windows=False) + trailing

    text = WIN_PATH_RE.sub(repl_win, text)
    text = UNIX_PATH_RE.sub(repl_unix, text)
    return text


def replace_handles_hashtags(text):
    def repl_handle(match):
        handle = split_camel(match.group(1)).replace("_", " ")
        return f"at {handle}"

    def repl_hash(match):
        tag = split_camel(match.group(1)).replace("_", " ")
        return f"hashtag {tag}"

    text = HANDLE_RE.sub(repl_handle, text)
    text = HASHTAG_RE.sub(repl_hash, text)
    return text


def replace_tech_terms(text, config):
    tech_terms = config.get("tech_pronunciations", {})
    for key in sorted(tech_terms.keys(), key=len, reverse=True):
        pattern = r"(?<!\w)" + re.escape(key) + r"(?!\w)"
        text = re.sub(pattern, tech_terms[key], text, flags=re.IGNORECASE)
    return text


def replace_ampersands(text):
    text = re.sub(r"(?<=\w)&(?=\w)", " and ", text)
    text = text.replace("&", " and ")
    return text


def replace_slashes(text):
    return re.sub(r"(?<=\w)/(?!\s)", " slash ", text)


def replace_pluses(text):
    return text.replace("+", " plus ")


def auto_spell_acronyms(text, config):
    if not config.get("auto_spell_acronyms", True):
        return text
    stoplist = {w.upper() for w in config.get("acronym_stoplist", [])}
    force = {w.upper() for w in config.get("acronym_force", [])}
    for key in config.get("tech_pronunciations", {}).keys():
        key_up = key.upper()
        if re.fullmatch(r"[A-Z0-9+/.-]+", key_up):
            force.add(key_up)

    def repl(match):
        token = match.group(0)
        token_up = token.upper()
        if token_up in stoplist:
            return token
        if token_up in force:
            return spell_letters(token)
        return token.lower()

    return re.sub(r"\b[A-Z]{2,6}\b", repl, text)


def normalize_bullets(text):
    lines = text.split("\n")
    out = []
    bullets = []

    def flush():
        for item in bullets:
            item = item.strip()
            if not item:
                continue
            if not re.search(r"[.!?]$", item):
                item += "."
            out.append(item)
        bullets.clear()

    for line in lines:
        m = BULLET_RE.match(line)
        if m:
            bullets.append(m.group(1))
        else:
            if bullets:
                flush()
            cleaned = line.strip()
            if cleaned:
                out.append(cleaned)

    if bullets:
        flush()

    return " ".join(out)


def replace_abbreviations(text, abbreviations):
    for k, v in abbreviations.items():
        pattern = r"(?<!\\w)" + re.escape(k) + r"(?!\\w)"
        text = re.sub(pattern, v, text, flags=re.IGNORECASE)
    return text


def handle_parentheses(text, policy):
    if policy == "strip":
        return re.sub(r"\([^)]*\)", "", text)
    if policy == "unwrap":
        return re.sub(r"\(([^)]*)\)", r" \1 ", text)
    if policy == "expand":
        return re.sub(r"\(([^)]*)\)", r", \1", text)
    return text


def normalize_whitespace(text):
    text = re.sub(r"[\t ]+", " ", text)
    text = re.sub(r"\s+([.,!?])", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def convert_explicit_sfx(text, allowed_tags):
    allowed = {t.strip("[]").lower(): t for t in allowed_tags}

    def repl(match):
        key = match.group(2).lower().replace("  ", " ").strip()
        key = key.replace("  ", " ")
        return allowed.get(key, "")

    return SFX_RE.sub(repl, text)


def protect_tags(text, allowed_tags):
    allowed = set(allowed_tags)
    placeholders = {}

    def repl(match):
        tag = match.group(0)
        if tag in allowed:
            key = f"__TAG{len(placeholders)}__"
            placeholders[key] = tag
            return key
        return ""

    text = re.sub(r"\[[a-z ]+\]", repl, text, flags=re.IGNORECASE)
    return text, placeholders


def restore_tags(text, placeholders):
    for key, tag in placeholders.items():
        text = text.replace(key, tag)
    return text


def normalize_text(text, config):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = convert_explicit_sfx(text, config.get("allowed_tags", []))
    text = normalize_bullets(text)

    text, placeholders = protect_tags(text, config.get("allowed_tags", []))

    text = replace_urls(text, config)
    text = replace_emails(text, config)
    text = replace_paths(text, config)
    text = replace_handles_hashtags(text)
    text = replace_big_o(text)

    paren_policy = config.get("paren_policy", "strip")
    text = handle_parentheses(text, paren_policy)

    abbreviations = config.get("abbreviations", {})
    if abbreviations:
        text = replace_abbreviations(text, abbreviations)

    text = replace_tech_terms(text, config)
    text = replace_ampersands(text)
    text = replace_pluses(text)
    text = replace_slashes(text)
    text = replace_ip_addresses(text, config)
    text = replace_versions(text)
    text = replace_mac_addresses(text)
    text = replace_hex_numbers(text)
    text = replace_hyphen_units(text)
    text = replace_minute_quantifiers(text)
    text = replace_units(text, config)

    text = replace_times(text, config)
    text = replace_ordinals(text)
    text = replace_decimals(text)
    text = replace_numbers(text)
    text = replace_minimum_phrases(text)
    text = auto_spell_acronyms(text, config)

    if config.get("strip_emoji", True):
        text = strip_emoji(text)
        text = "".join(ch for ch in text if unicodedata.category(ch) != "Cs")

    text = normalize_whitespace(text)
    text = restore_tags(text, placeholders)
    return text
