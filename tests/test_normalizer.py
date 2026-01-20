import pytest

from sayable.config import load_config
from sayable.normalizer import normalize_text


@pytest.fixture()
def cfg():
    return load_config(None)


def test_time_and_parentheses(cfg):
    text = "We meet at 12:00 pm (be on time)"
    assert normalize_text(text, cfg) == "We meet at twelve o'clock p m, be on time"


def test_acronyms_and_caps(cfg):
    text = "GPU MUCH FAST"
    assert normalize_text(text, cfg) == "g p u much fast"


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
