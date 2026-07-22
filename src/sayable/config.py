1|import json
2|from copy import deepcopy
3|
4|SUPPORTED_TAGS = [
5|    "[clear throat]",
6|    "[sigh]",
7|    "[shush]",
8|    "[cough]",
9|    "[groan]",
10|    "[sniff]",
11|    "[gasp]",
12|]
13|
14|LABEL_TO_TAG = {
15|    "clear_throat": "[clear throat]",
16|    "sigh": "[sigh]",
17|    "shush": "[shush]",
18|    "cough": "[cough]",
19|    "groan": "[groan]",
20|    "sniff": "[sniff]",
21|    "gasp": "[gasp]",
22|    "none": "",
23|}
24|
25|
26|class ConfigError(ValueError):
27|    """Raised when Sayable configuration is invalid."""
28|
29|DEFAULT_CONFIG = {
30|    "time_style": "12h",
31|    "time_zero": "oclock",
32|    "time_include_am_pm": True,
33|    "minute_leading_zero": "oh",
34|    "paren_policy": "expand",
35|    "strip_emoji": True,
36|    "tagger_enabled": True,
37|    "tag_min_confidence": 0.3,
38|    "tag_position": "prefix",
39|    "unknown_tag_policy": "preserve",
40|    "disabled_tags": ["[laugh]", "[chuckle]"],
41|    "tagger_strategy": "nb",
42|    "tag_max_per_chunk": 3,
43|    "url_policy": "domain",
44|    "url_include_scheme": False,
45|    "url_read_query": False,
46|    "url_read_fragment": False,
47|    "url_include_port": True,
48|    "path_policy": "speak",
49|    "ip_digit_style": "single",
50|    "date_order": "mdy",
51|    "year_style": "auto",
52|    "currency_style": "natural",
53|    "phone_digit_style": "grouped",
54|    "markdown_policy": "plain",
55|    "code_block_policy": "summarize",
56|    "output_mode": "plain",
57|    "ssml_tag_policy": "remove",
58|    "ssml_break_markers": {"[pause]": {"time": "500ms"}},
59|    "chunk_size": 0,
60|    "chunk_separator": "\n\n",
61|    "auto_spell_acronyms": True,
62|    "acronym_stoplist": [
63|        "AM",
64|        "PM",
65|        "OK",
66|        "US",
67|        "UK",
68|    ],
69|    "acronym_force": [
70|        "AI",
71|        "ML",
72|        "NLP",
73|        "LLM",
74|        "ASR",
75|        "TTS",
76|        "API",
77|        "SDK",
78|        "HTTP",
79|        "HTTPS",
80|        "URL",
81|        "URI",
82|        "DNS",
83|        "IP",
84|        "TCP",
85|        "UDP",
86|        "SSH",
87|        "SSL",
88|        "TLS",
89|        "JSON",
90|        "XML",
91|        "HTML",
92|        "CSS",
93|        "JS",
94|        "TS",
95|        "SQL",
96|        "GPU",
97|        "CPU",
98|        "RAM",
99|        "VRAM",
100|        "SSD",
101|        "HDD",
102|        "OS",
103|        "UI",
104|        "UX",
105|        "CLI",
106|        "IDE",
107|        "CI",
108|        "CD",
109|        "QA",
110|        "SaaS",
111|        "PaaS",
112|        "IaaS",
113|        "IoT",
114|        "CUDA",
115|        "C++",
116|        "C#",
117|        "F#",
118|        "RTX",
119|        "GPT",
120|        "UUID",
121|        "GUID",
122|        "ASCII",
123|        "UTF",
124|        "REST",
125|        "RGB",
126|        "BGR",
127|    ],
128|    "abbreviations": {
129|        "e.g.": "for example",
130|        "i.e.": "that is",
131|        "etc.": "et cetera",
132|        "vs.": "versus",
133|        "mr.": "mister",
134|        "mrs.": "missus",
135|        "dr.": "doctor",
136|    },
137|    "tech_pronunciations": {
138|        "AI": "A I",
139|        "A.I.": "A I",
140|        "ML": "m l",
141|        "DL": "d l",
142|        "LLM": "l l m",
143|        "NLP": "n l p",
144|        "ASR": "a s r",
145|        "TTS": "t t s",
146|        "API": "a p i",
147|        "SDK": "s d k",
148|        "HTTP": "h t t p",
149|        "HTTPS": "h t t p s",
150|        "URL": "u r l",
151|        "URI": "u r i",
152|        "DNS": "d n s",
153|        "IP": "i p",
154|        "TCP": "t c p",
155|        "UDP": "u d p",
156|        "SSH": "s s h",
157|        "SSL": "s s l",
158|        "TLS": "t l s",
159|        "JSON": "j s o n",
160|        "XML": "x m l",
161|        "HTML": "h t m l",
162|        "CSS": "c s s",
163|        "JS": "j s",
164|        "TS": "t s",
165|        "SQL": "s q l",
166|        "GPU": "g p u",
167|        "CPU": "c p u",
168|        "RAM": "r a m",
169|        "VRAM": "v r a m",
170|        "SSD": "s s d",
171|        "HDD": "h d d",
172|        "OS": "o s",
173|        "UI": "u i",
174|        "UX": "u x",
175|        "CLI": "c l i",
176|        "IDE": "i d e",
177|        "CI": "c i",
178|        "CD": "c d",
179|        "CI/CD": "c i slash c d",
180|        "QA": "q a",
181|        "SaaS": "s a a s",
182|        "PaaS": "p a a s",
183|        "IaaS": "i a a s",
184|        "IoT": "i o t",
185|        "CUDA": "koo da",
186|        "RTX": "r t x",
187|        "GPT": "g p t",
188|        "C++": "c plus plus",
189|        "C#": "c sharp",
190|        "F#": "f sharp",
191|        ".NET": "dot net",
192|        "Node.js": "node j s",
193|        "Next.js": "next j s",
194|        "React.js": "react j s",
195|        "Vue.js": "vue j s",
196|        "TypeScript": "type script",
197|        "JavaScript": "java script",
198|        "K8s": "k eight s",
199|        "K3s": "k three s",
200|        "OAuth": "o auth",
201|        "JWT": "j w t",
202|        "gRPC": "g r p c",
203|        "openmontage": "open mahn tahzh",
204|        "Open Montage": "open mahn tahzh",
205|        "UTF-8": "u t f eight",
206|        "UTF8": "u t f eight",
207|        "ASCII": "a s c i i",
208|    },
209|    "domain_pronunciations": {
210|        "com": "com",
211|        "net": "net",
212|        "org": "org",
213|        "io": "i o",
214|        "ai": "A I",
215|        "dev": "dev",
216|        "app": "app",
217|        "edu": "e d u",
218|        "gov": "gov",
219|        "co": "co",
220|        "us": "u s",
221|        "uk": "u k",
222|        "gg": "g g",
223|        "tv": "t v",
224|        "me": "me",
225|        "ly": "l y",
226|    },
227|    "unit_pronunciations": {
228|        "kb": "kilobytes",
229|        "mb": "megabytes",
230|        "gb": "gigabytes",
231|        "tb": "terabytes",
232|        "kib": "kibibytes",
233|        "mib": "mebibytes",
234|        "gib": "gibibytes",
235|        "tib": "tebibytes",
236|        "hz": "hertz",
237|        "khz": "kilohertz",
238|        "mhz": "megahertz",
239|        "ghz": "gigahertz",
240|        "kbps": "kilobits per second",
241|        "mbps": "megabits per second",
242|        "gbps": "gigabits per second",
243|        "ms": "milliseconds",
244|        "s": "seconds",
245|        "sec": "seconds",
246|        "secs": "seconds",
247|        "min": "minutes",
248|        "mins": "minutes",
249|        "hr": "hours",
250|        "hrs": "hours",
251|        "fps": "frames per second",
252|        "dpi": "dots per inch",
253|        "ppi": "pixels per inch",
254|        "px": "pixels",
255|        "%": "percent",
256|    },
257|    "allowed_tags": SUPPORTED_TAGS,
258|    "label_to_tag": LABEL_TO_TAG,
259|}
260|
261|
262|ENUM_FIELDS = {
263|    "time_style": {"12h", "24h"},
264|    "time_zero": {"oclock", "hundred"},
265|    "minute_leading_zero": {"oh", "zero"},
266|    "paren_policy": {"strip", "unwrap", "expand", "preserve"},
267|    "tag_position": {"prefix", "suffix"},
268|    "unknown_tag_policy": {"preserve", "strip", "escape"},
269|    "tagger_strategy": {"rules", "nb", "rules_nb"},
270|    "url_policy": {"domain", "full", "preserve"},
271|    "path_policy": {"speak", "preserve", "strip"},
272|    "ip_digit_style": {"single", "grouped"},
273|    "date_order": {"mdy", "dmy", "ymd"},
274|    "year_style": {"auto", "digits", "cardinal"},
275|    "currency_style": {"natural"},
276|    "phone_digit_style": {"grouped", "single"},
277|    "markdown_policy": {"plain", "speak", "preserve"},
278|    "code_block_policy": {"summarize", "speak", "strip"},
279|    "output_mode": {"plain", "chatterbox", "ssml"},
280|    "ssml_tag_policy": {"remove", "speak", "preserve"},
281|}
282|
283|BOOL_FIELDS = {
284|    "time_include_am_pm",
285|    "strip_emoji",
286|    "tagger_enabled",
287|    "url_include_scheme",
288|    "url_read_query",
289|    "url_read_fragment",
290|    "url_include_port",
291|    "auto_spell_acronyms",
292|}
293|
294|LIST_FIELDS = {"allowed_tags", "disabled_tags", "acronym_stoplist", "acronym_force"}
295|DICT_FIELDS = {
296|    "label_to_tag",
297|    "abbreviations",
298|    "tech_pronunciations",
299|    "domain_pronunciations",
300|    "unit_pronunciations",
301|    "ssml_break_markers",
302|}
303|
304|
305|def _fail(field, message):
306|    raise ConfigError(f"Invalid config field '{field}': {message}")
307|
308|
309|def _check_string_list(config, field):
310|    value = config.get(field)
311|    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
312|        _fail(field, "expected a list of strings")
313|
314|
315|def _check_string_dict(config, field):
316|    value = config.get(field)
317|    if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
318|        _fail(field, "expected a dictionary of string keys and string values")
319|
320|
321|def _check_break_markers(config):
322|    markers = config.get("ssml_break_markers")
323|    if not isinstance(markers, dict):
324|        _fail("ssml_break_markers", "expected a dictionary")
325|    for marker, setting in markers.items():
326|        if not isinstance(marker, str):
327|            _fail("ssml_break_markers", "marker keys must be strings")
328|        if isinstance(setting, str):
329|            continue
330|        if not isinstance(setting, dict):
331|            _fail("ssml_break_markers", "marker values must be strings or dictionaries")
332|        if not any(key in setting for key in ("time", "strength")):
333|            _fail("ssml_break_markers", "marker dictionaries must include time or strength")
334|        for key, value in setting.items():
335|            if key not in {"time", "strength"}:
336|                _fail("ssml_break_markers", f"unsupported marker option {key!r}")
337|            if not isinstance(value, str):
338|                _fail("ssml_break_markers", "marker options must be strings")
339|
340|
341|def validate_config(config):
342|    if not isinstance(config, dict):
343|        raise ConfigError("Config must be a dictionary")
344|
345|    for field, accepted in ENUM_FIELDS.items():
346|        value = config.get(field)
347|        if value not in accepted:
348|            accepted_values = ", ".join(sorted(accepted))
349|            _fail(field, f"expected one of: {accepted_values}")
350|
351|    for field in BOOL_FIELDS:
352|        if not isinstance(config.get(field), bool):
353|            _fail(field, "expected a boolean")
354|
355|    for field in LIST_FIELDS:
356|        _check_string_list(config, field)
357|
358|    for field in DICT_FIELDS - {"ssml_break_markers"}:
359|        _check_string_dict(config, field)
360|    _check_break_markers(config)
361|
362|    tag_min_confidence = config.get("tag_min_confidence")
363|    if not isinstance(tag_min_confidence, (int, float)) or isinstance(tag_min_confidence, bool):
364|        _fail("tag_min_confidence", "expected a number from 0 to 1")
365|    if not 0 <= tag_min_confidence <= 1:
366|        _fail("tag_min_confidence", "expected a number from 0 to 1")
367|
368|    for field in ("tag_max_per_chunk", "chunk_size"):
369|        value = config.get(field)
370|        if not isinstance(value, int) or isinstance(value, bool):
371|            _fail(field, "expected a non-negative integer")
372|        if value < 0:
373|            _fail(field, "expected a non-negative integer")
374|
375|    chunk_separator = config.get("chunk_separator")
376|    if not isinstance(chunk_separator, str):
377|        _fail("chunk_separator", "expected a string")
378|
379|    allowed = set(config.get("allowed_tags", []))
380|    for tag in config.get("disabled_tags", []):
381|        if tag in allowed:
382|            _fail("disabled_tags", f"{tag!r} cannot also be allowed")
383|
384|    for label, tag in config.get("label_to_tag", {}).items():
385|        if label != "none" and tag and tag not in allowed:
386|            _fail("label_to_tag", f"{label!r} maps to unsupported tag {tag!r}")
387|
388|    return config
389|
390|
391|def load_config(path):
392|    if not path:
393|        return validate_config(deepcopy(DEFAULT_CONFIG))
394|    with open(path, "r", encoding="utf-8") as f:
395|        data = json.load(f)
396|    if not isinstance(data, dict):
397|        raise ConfigError("Config file must contain a JSON object")
398|    cfg = deepcopy(DEFAULT_CONFIG)
399|    cfg.update(data)
400|    return validate_config(cfg)
401|