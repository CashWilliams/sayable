1|import pytest
2|
3|from sayable.config import load_config
4|from sayable.chunker import chunk_text
5|from sayable.normalizer import normalize_text
6|from sayable.output import format_output
7|
8|
9|@pytest.fixture()
10|def cfg():
11|    return load_config(None)
12|
13|
14|def test_time_and_parentheses(cfg):
15|    text = "We meet at 12:00 pm (be on time)"
16|    assert normalize_text(text, cfg) == "We meet at twelve o'clock p m, be on time"
17|
18|
19|def test_acronyms_and_caps(cfg):
20|    text = "GPU MUCH FAST"
21|    assert normalize_text(text, cfg) == "g p u much fast"
22|
23|
24|def test_ai_and_dotted_ai(cfg):
25|    text = "AI, A.I., and ai are related"
26|    assert normalize_text(text, cfg) == "A I, A I, and A I are related"
27|
28|
29|def test_lowercase_rest_in_natural_prose_is_unchanged(cfg):
30|    text = "the rest of the story"
31|    assert normalize_text(text, cfg) == "the rest of the story"
32|
33|
34|def test_openmontage_pronunciation_variants(cfg):
35|    text = "Use openmontage or Open Montage for this."
36|    assert (
37|        normalize_text(text, cfg)
38|        == "Use open mahn tahzh or open mahn tahzh for this."
39|    )
40|
41|
42|def test_minutes_and_minimum(cfg):
43|    text = "This takes a few min. It is at the min. It takes 2-min."
44|    assert (
45|        normalize_text(text, cfg)
46|        == "This takes a few minutes. It is at the minimum. It takes two minutes."
47|    )
48|
49|
50|def test_units_versions_ip(cfg):
51|    text = "v1.2.3 3.5GHz 256GB IP 192.168.0.1"
52|    assert (
53|        normalize_text(text, cfg)
54|        == "version one point two point three three point five gigahertz two hundred fifty six gigabytes i p one nine two dot one six eight dot zero dot one"
55|    )
56|
57|
58|def test_email_and_url(cfg):
59|    text = "Email test.user+ai@example.com and visit https://example.com"
60|    assert (
61|        normalize_text(text, cfg)
62|        == "Email test dot user plus A I at example dot com and visit example dot com"
63|    )
64|
65|
66|def test_unknown_tags_are_preserved_by_default(cfg):
67|    assert normalize_text("hello [laugh] there [sigh]", cfg) == "hello [laugh] there [sigh]"
68|
69|
70|def test_unknown_tags_can_be_stripped(cfg):
71|    cfg["unknown_tag_policy"] = "strip"
72|    assert normalize_text("hello [laugh] there [sigh]", cfg) == "hello there [sigh]"
73|
74|
75|def test_regression_developer_text_fixture(cfg):
76|    cfg["url_policy"] = "preserve"
77|    cfg["path_policy"] = "preserve"
78|    text = "Run `uv run pytest` against /tmp/app on v1.2.3, then curl https://example.com."
79|    out = normalize_text(text, cfg)
80|    assert "/tmp/app" in out
81|    assert "https://example.com." in out
82|    assert "version one point two point three" in out
83|
84|
85|def test_regression_ai_prose_fixture(cfg):
86|    text = "- AI updates (brief)\n- Keep [sigh] exactly\nOK?"
87|    out = normalize_text(text, cfg)
88|    assert "A I updates, brief." in out
89|    assert "[sigh]" in out
90|    assert out.endswith("OK?")
91|
92|
93|def test_dates_currency_fractions_percent_and_phone(cfg):
94|    text = "On 2026-05-23 pay $12.50, use 1/2 now, hit 42%, call 555-123-4567."
95|    assert (
96|        normalize_text(text, cfg)
97|        == "On May twenty third twenty twenty six pay twelve dollars and fifty cents, use one half now, hit forty two percent, call five five five, one two three, four five six seven."
98|    )
99|
100|
101|def test_slash_date_and_year_range(cfg):
102|    text = "From 1999-2001, ship on 05/23/2026."
103|    assert (
104|        normalize_text(text, cfg)
105|        == "From nineteen ninety nine to two thousand one, ship on May twenty third twenty twenty six."
106|    )
107|
108|
109|def test_markdown_cleanup(cfg):
110|    text = "# Title\nSee [docs](https://example.com).\nRun `uv run pytest`.\n```py\nprint('x')\n```"
111|    assert (
112|        normalize_text(text, cfg)
113|        == "Title See docs. Run uv run pytest. code block omitted"
114|    )
115|
116|
117|def test_fenced_code_speak_omits_language_marker(cfg):
118|    cfg["code_block_policy"] = "speak"
119|    text = "```bash\nuv run pytest\n```"
120|    out = normalize_text(text, cfg)
121|    assert out == "code block uv run pytest"
122|    assert "bash" not in out
123|
124|
125|def test_stack_trace_policy(cfg):
126|    text = "Traceback (most recent call last):\n  File \"x.py\", line 1, in <module>\nValueError: bad"
127|    assert normalize_text(text, cfg) == "stack trace omitted"
128|    cfg["code_block_policy"] = "strip"
129|    assert normalize_text(text, cfg) == ""
130|
131|
132|def test_markdown_table_cleanup_and_preserve_mode(cfg):
133|    table = "| Name | Value |\n| --- | --- |\n| API | v1.2.3 |"
134|    assert normalize_text(table, cfg) == "Name, Value a p i, version one point two point three"
135|    cfg["markdown_policy"] = "preserve"
136|    assert normalize_text("`uv run pytest`", cfg) == "`uv run pytest`"
137|
138|
139|def test_markdown_speak_link_includes_url(cfg):
140|    cfg["markdown_policy"] = "speak"
141|    assert normalize_text("[docs](https://example.com)", cfg) == "docs, example dot com"
142|
143|
144|def test_chunk_text(cfg):
145|    cfg["chunk_size"] = 18
146|    assert chunk_text("One sentence. Two sentence. Three sentence.", cfg) == [
147|        "One sentence.",
148|        "Two sentence.",
149|        "Three sentence.",
150|    ]
151|
152|
153|def test_chunk_text_prefers_paragraph_boundaries(cfg):
154|    cfg["chunk_size"] = 80
155|    assert chunk_text("First paragraph.\n\nSecond paragraph.", cfg) == [
156|        "First paragraph.",
157|        "Second paragraph.",
158|    ]
159|
160|
161|def test_chunk_text_preserves_protected_spans(cfg):
162|    cfg["chunk_size"] = 16
163|    text = (
164|        "Use [clear throat] and https://example.com/path plus "
165|        "test.user@example.com /tmp/project/file.txt v1.2.3 192.168.0.1 "
166|        "3.14 555-123-4567 $12.50."
167|    )
168|    chunks = chunk_text(text, cfg)
169|    joined = " ".join(chunks)
170|    for span in [
171|        "[clear throat]",
172|        "https://example.com/path",
173|        "test.user@example.com",
174|        "/tmp/project/file.txt",
175|        "v1.2.3",
176|        "192.168.0.1",
177|        "3.14",
178|        "555-123-4567",
179|        "$12.50",
180|    ]:
181|        assert span in chunks or span in joined
182|        assert any(span in chunk for chunk in chunks)
183|
184|
185|def test_chunk_text_allows_oversized_protected_span(cfg):
186|    cfg["chunk_size"] = 10
187|    chunks = chunk_text("before https://example.com/very/long/path after", cfg)
188|    assert "https://example.com/very/long/path" in chunks
189|
190|
191|def test_ssml_output(cfg):
192|    cfg["output_mode"] = "ssml"
193|    assert format_output("A < B & C", cfg) == "<speak>A &lt; B &amp; C</speak>"
194|
195|
196|def test_ssml_removes_tags_by_default(cfg):
197|    cfg["output_mode"] = "ssml"
198|    assert format_output("hello [sigh] there", cfg) == "<speak>hello there</speak>"
199|
200|
201|def test_ssml_tag_policy_variants_and_unknown_tags(cfg):
202|    cfg["output_mode"] = "ssml"
203|    cfg["ssml_tag_policy"] = "speak"
204|    assert format_output("hello [sigh]", cfg) == "<speak>hello sigh</speak>"
205|
206|    cfg["ssml_tag_policy"] = "preserve"
207|    assert format_output("hello [unknown <tag>]", cfg) == "<speak>hello [unknown &lt;tag&gt;]</speak>"
208|
209|
210|def test_ssml_break_marker_conversion(cfg):
211|    cfg["output_mode"] = "ssml"
212|    cfg["ssml_break_markers"] = {"[pause]": {"time": "750ms"}}
213|    assert format_output("hello [pause] there", cfg) == '<speak>hello <break time="750ms"/> there</speak>'
214|
215|    cfg["output_mode"] = "plain"
216|    assert format_output("hello [pause] there", cfg) == "hello [pause] there"
217|