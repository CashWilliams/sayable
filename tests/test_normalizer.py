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
    text = "AI, A.I., and ai are related"
    assert normalize_text(text, cfg) == "A I, A I, and A I are related"


def test_lowercase_rest_in_natural_prose_is_unchanged(cfg):
    text = "the rest of the story"
    assert normalize_text(text, cfg) == "the rest of the story"


def test_openmontage_pronunciation_variants(cfg):
    text = "Use openmontage or Open Montage for this."
    assert (
        normalize_text(text, cfg)
        == "Use open mahn tahzh or open mahn tahzh for this."
    )


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


def test_bare_decimals_are_not_versions(cfg):
    assert normalize_text("The value is 3.14 and also 3.5.", cfg) == (
        "The value is three point one four and also three point five."
    )


def test_dotted_software_versions_still_speak_as_versions(cfg):
    assert normalize_text("Released v1.2.3 and 1.2.3 today.", cfg) == (
        "Released version one point two point three and version one point two point three today."
    )


def test_abbreviations_do_not_match_inside_words(cfg):
    cfg["abbreviations"] = {"ok": "okay", "e.g.": "for example"}
    assert normalize_text("booking the room, e.g. now", cfg) == (
        "booking the room, for example now"
    )


def test_email_and_url(cfg):
    text = "Email test.user+ai@example.com and visit https://example.com"
    assert (
        normalize_text(text, cfg)
        == "Email test dot user plus A I at example dot com and visit example dot com"
    )


def test_unknown_tags_are_preserved_by_default(cfg):
    assert normalize_text("hello [laugh] there [sigh]", cfg) == "hello [laugh] there [sigh]"


def test_unknown_tags_can_be_stripped(cfg):
    cfg["unknown_tag_policy"] = "strip"
    assert normalize_text("hello [laugh] there [sigh]", cfg) == "hello there [sigh]"


def test_regression_developer_text_fixture(cfg):
    cfg["url_policy"] = "preserve"
    cfg["path_policy"] = "preserve"
    text = "Run `uv run pytest` against /tmp/app on v1.2.3, then curl https://example.com."
    out = normalize_text(text, cfg)
    assert "/tmp/app" in out
    assert "https://example.com." in out
    assert "version one point two point three" in out


def test_regression_ai_prose_fixture(cfg):
    text = "- AI updates (brief)\n- Keep [sigh] exactly\nOK?"
    out = normalize_text(text, cfg)
    assert "A I updates, brief." in out
    assert "[sigh]" in out
    assert out.endswith("OK?")


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


def test_ymd_slash_dates(cfg):
    cfg["date_order"] = "ymd"
    assert normalize_text("ship on 2026/05/23.", cfg) == (
        "ship on May twenty third twenty twenty six."
    )
    assert normalize_text("ship on 26/05/23.", cfg) == (
        "ship on May twenty third twenty twenty six."
    )


def test_impossible_dates_are_left_unchanged(cfg):
    out = normalize_text("On 2026-13-40 we leave.", cfg)
    assert "2026-13-40" in out
    assert "thirteenth" not in out.lower()
    assert "fortieth" not in out.lower()


def test_markdown_cleanup(cfg):
    text = "# Title\nSee [docs](https://example.com).\nRun `uv run pytest`.\n```py\nprint('x')\n```"
    assert (
        normalize_text(text, cfg)
        == "Title See docs. Run uv run pytest. code block omitted"
    )


def test_fenced_code_speak_omits_language_marker(cfg):
    cfg["code_block_policy"] = "speak"
    text = "```bash\nuv run pytest\n```"
    out = normalize_text(text, cfg)
    assert out == "code block uv run pytest"
    assert "bash" not in out


def test_stack_trace_policy(cfg):
    text = "Traceback (most recent call last):\n  File \"x.py\", line 1, in <module>\nValueError: bad"
    assert normalize_text(text, cfg) == "stack trace omitted"
    cfg["code_block_policy"] = "strip"
    assert normalize_text(text, cfg) == ""


def test_markdown_table_cleanup_and_preserve_mode(cfg):
    table = "| Name | Value |\n| --- | --- |\n| API | v1.2.3 |"
    assert normalize_text(table, cfg) == "Name, Value a p i, version one point two point three"
    cfg["markdown_policy"] = "preserve"
    assert normalize_text("`uv run pytest`", cfg) == "`uv run pytest`"


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


def test_chunk_text_prefers_paragraph_boundaries(cfg):
    cfg["chunk_size"] = 80
    assert chunk_text("First paragraph.\n\nSecond paragraph.", cfg) == [
        "First paragraph.",
        "Second paragraph.",
    ]


def test_chunk_text_preserves_protected_spans(cfg):
    cfg["chunk_size"] = 16
    text = (
        "Use [clear throat] and https://example.com/path plus "
        "test.user@example.com /tmp/project/file.txt v1.2.3 192.168.0.1 "
        "3.14 555-123-4567 $12.50."
    )
    chunks = chunk_text(text, cfg)
    joined = " ".join(chunks)
    for span in [
        "[clear throat]",
        "https://example.com/path",
        "test.user@example.com",
        "/tmp/project/file.txt",
        "v1.2.3",
        "192.168.0.1",
        "3.14",
        "555-123-4567",
        "$12.50",
    ]:
        assert span in chunks or span in joined
        assert any(span in chunk for chunk in chunks)


def test_chunk_text_allows_oversized_protected_span(cfg):
    cfg["chunk_size"] = 10
    chunks = chunk_text("before https://example.com/very/long/path after", cfg)
    assert "https://example.com/very/long/path" in chunks


def test_ssml_output(cfg):
    cfg["output_mode"] = "ssml"
    assert format_output("A < B & C", cfg) == "<speak>A &lt; B &amp; C</speak>"


def test_ssml_removes_tags_by_default(cfg):
    cfg["output_mode"] = "ssml"
    assert format_output("hello [sigh] there", cfg) == "<speak>hello there</speak>"


def test_ssml_tag_policy_variants_and_unknown_tags(cfg):
    cfg["output_mode"] = "ssml"
    cfg["ssml_tag_policy"] = "speak"
    assert format_output("hello [sigh]", cfg) == "<speak>hello sigh</speak>"

    cfg["ssml_tag_policy"] = "preserve"
    assert format_output("hello [unknown <tag>]", cfg) == "<speak>hello [unknown &lt;tag&gt;]</speak>"


def test_ssml_break_marker_conversion(cfg):
    cfg["output_mode"] = "ssml"
    cfg["ssml_break_markers"] = {"[pause]": {"time": "750ms"}}
    assert format_output("hello [pause] there", cfg) == '<speak>hello <break time="750ms"/> there</speak>'

    cfg["output_mode"] = "plain"
    assert format_output("hello [pause] there", cfg) == "hello [pause] there"
