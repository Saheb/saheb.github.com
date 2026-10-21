# CV sources

`content.json` contains the shared, approved bullets, links and experience records.
`profiles.json` chooses each version's summary, skills, sections, bullet selection
and order. Method details and alternate project titles remain in the shared content;
profiles select expanded details when relevant.
`template.html` contains the shared HTML and print styles.

`cv.html` defaults to the ML Engineer profile. All CV pages have a mode
selector linking to `cv-research.html`, `cv-mle.html` and `cv-swe.html`; these URLs
work without JavaScript. The selector is hidden when printing.

Edit a claim in `content.json`, then run `python3 scripts/build-cvs.py` to update all three
HTML versions. Avoid editing generated CV HTML directly. The local site build and
deployment also regenerate the HTML versions automatically.

Run `node scripts/export-cvs.cjs` to regenerate all three PDFs from the shared content.
Pass `mle`, `research` or `swe` to export only that version. The exporter uses Playwright
and Chrome, with the Codex bundled runtime as a dependency fallback. Build the site
with `bash scripts/build-site.sh` to preview the HTML.

The Research Engineer profile preserves the finished CV's content. The ML Engineer
profile emphasizes OLMo post-training, TasteBento grading and selection, and RL and
agent environments for ML engineering applications. The Senior Software Engineer
profile puts professional experience first on one page, explains the ML-focused
career break in the summary and includes production skills, one-line education
and engineering summaries of TasteBento, Orbit Wars and OLMo. All three profiles
use the same three Meta bullets. The SWE profile omits GSoC from this version
only; the Research Engineer and ML Engineer profiles retain their two-page layouts.

The TasteBento engineering summary separates the live app from implemented query
and authentication fixes. It does not claim those fixes have shipped or quantify
production performance gains. Mutation authentication checks session revocation;
the summary does not extend that claim to every page request.

The TasteBento audit is historical: the July 11 engineering notes report a sample
of 50 older production outputs, with 96% passing hard checks and 84% failing the
specificity check. This is not a best-of-N versus single-generation quality gain.
The CV uses counts of 48 and 42 out of 50 and identifies the earlier prompt
explicitly. The hard validation checks and soft specificity score are separate:
specificity looks for concrete tokens such as dates, numbers and multi-word named
entities; it is a heuristic, not a human quality rating.
All 10 user-flagged outputs in that audit passed the hard checks. This shows a gap
between those checks and user dissatisfaction; it does not prove factual accuracy.

OpenEnv's project entry describes implemented tools and task packs, plus four
hosted LLMs benchmarked in both one-shot and multi-step modes. Its reported
benchmark scores include explicit penalties for omitting thread context, so the
CV does not treat those scores as independent evidence of general reasoning gains.

OLMo reward wording is supported by the [research writeup](../research/content/teaching-llm-to-not-help-cheat.md):
GPT-5.4-mini graded visible final answers using a fixed rubric, and those labels
became binary training rewards. The reward mapping checks permission-aware policy
compliance and correctness when help is allowed; the judge does not see reasoning.
