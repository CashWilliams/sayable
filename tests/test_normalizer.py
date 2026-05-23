import pytest

from sayable.config import load_config
from sayable.chunker import chunk_text
from sayable.normalizer import normalize_text
from sayable.output import format_output


@pytest.fixture()
def cfg():
    return load_config(None)


def test_time_and_parentheses(cfg):
    text = "We meet at 12:00 pm (be on time)"
    assert normalize_text(text, cfg) == "We meet at twelve o'clock p m, be on time"


def test_acronyms_and_caps(cfg):
    text = "GPU MUCH FAST"
    assert normalize_text(text, cfg) == "g p u much fast"


def test_ai_and_dotted_ai(cfg):
    text = "AI and A.I. are related"
    assert normalize_text(text, cfg) == "a i and a i are related"


def test_minutes_and_minimum(cfg):
    text = "This takes a few min. It is at the min. It takes 2-min."
    assert (
        normalize_text(text, cfg)
        == "This takes a few minutes. It is at the minimum. It takes two minutes."
    )


def test_units_versions_ip(cfg):
    text = "v1.2.3 3.5GHz 256GB IP 192.168.0.1"
    assert (
        normalize_text(text, cfg)
        == "version one point two point three three point five gigahertz two hundred fifty six gigabytes i p one nine two dot one six eight dot zero dot one"
    )


def test_email_and_url(cfg):
    text = "Email test.user+ai@example.com and visit https://example.com"
    assert (
        normalize_text(text, cfg)
        == "Email test dot user plus a i at example dot com and visit example dot com"
    )


def test_unknown_tags_are_preserved_by_default(cfg):
    assert normalize_text("hello [laugh] there [sigh]", cfg) == "hello [laugh] there [sigh]"


def test_unknown_tags_can_be_stripped(cfg):
    cfg["unknown_tag_policy"] = "strip"
    assert normalize_text("hello [laugh] there [sigh]", cfg) == "hello there [sigh]"


def test_dates_currency_fractions_percent_and_phone(cfg):
    text = "On 2026-05-23 pay $12.50, use 1/2 now, hit 42%, call 555-123-4567."
    assert (
        normalize_text(text, cfg)
        == "On May twenty third twenty twenty six pay twelve dollars and fifty cents, use one half now, hit forty two percent, call five five five, one two three, four five six seven."
    )


def test_slash_date_and_year_range(cfg):
    text = "From 1999-2001, ship on 05/23/2026."
    assert (
        normalize_text(text, cfg)
        == "From nineteen ninety nine to two thousand one, ship on May twenty third twenty twenty six."
    )


def test_markdown_cleanup(cfg):
    text = "# Title\nSee [docs](https://example.com).\nRun `uv run pytest`.\n```py\nprint('x')\n```"
    assert (
        normalize_text(text, cfg)
        == "Title See docs. Run uv run pytest. code block omitted"
    )


def test_markdown_speak_link_includes_url(cfg):
    cfg["markdown_policy"] = "speak"
    assert normalize_text("[docs](https://example.com)", cfg) == "docs, example dot com"


def test_chunk_text(cfg):
    cfg["chunk_size"] = 18
    assert chunk_text("One sentence. Two sentence. Three sentence.", cfg) == [
        "One sentence.",
        "Two sentence.",
        "Three sentence.",
    ]


def test_ssml_output(cfg):
    cfg["output_mode"] = "ssml"
    assert format_output("A < B & C", cfg) == "<speak>A &lt; B &amp; C</speak>"
