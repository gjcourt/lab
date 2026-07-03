---
title: 'EDGAR 10-K Automated Analysis Engine'
number: '04-016'
category: 'finance-analysis'
difficulty: 'Hard'
time_commitment: 'Months'
target_skills:
  'Go or Python, SEC EDGAR API, XBRL/companyfacts JSON, financial-statement analysis,
  quality-of-earnings, LLM synthesis (Claude API)'
status: 'Not Started'
depends_on:
  - external/edgar
  - external/anthropic-api
  - external/fred
---

# EDGAR 10-K Automated Analysis Engine

## Description

A tool that takes a ticker (or CIK), pulls the latest 10-K from SEC EDGAR, and produces the **full
fundamental + quality-of-earnings analysis** — the same analytical loop a human analyst runs by
hand: reconstruct the three statements, compute the ratio families, derive free cash flow, run the
quality-of-earnings checks, pull the "why" out of the MD&A, flag the red flags, and synthesize a
plain-English verdict. Output is a structured report (JSON + rendered Markdown/HTML) that plugs into
the personal finance workbench.

This is the productized version of a manual analysis done in a tutoring session (2026-07-02):
pulling Hershey's FY2025 10-K, spotting the −14pp gross-margin collapse, tracing it to cocoa via the
MD&A, adjusting for the $491M derivative mark-to-market (quality-of-earnings), and confirming the
story against the commodity itself and against peers (Mondelez, Tootsie Roll). The goal here is to
codify that loop so it runs on any filer in minutes.

**Relation to existing projects:** subsumes and extends `04-001` (XBRL parser — the ingestion layer)
and overlaps with `04-005` (SEC filing sentiment via LLMs — the MD&A layer). If `04-001` is built
first, reuse it as the ingestion module; otherwise this project includes a lean ingestion path off
the EDGAR JSON APIs (no raw XBRL parsing required for the structured facts).

## The analysis pipeline (what "full analysis" means)

Each stage mirrors the manual loop and should be an independently testable module.

1. **Ingest.** Resolve ticker → CIK (`company_tickers.json`), pull the latest 10-K's structured
   financial facts (`companyfacts`), the filing index (`submissions`), and the primary 10-K HTML
   document (for MD&A + footnotes). Multi-year history comes free from `companyfacts`.
2. **Build the three statements.** Normalize the us-gaap XBRL tags into a clean, multi-year Income
   Statement / Balance Sheet / Cash Flow. Handle tag drift (companies use different tags for the
   same line — e.g. `Revenues` vs `RevenueFromContractWithCustomerExcludingAssessedTax`) via a
   tag-alias map with fallbacks.
3. **Ratios.** Liquidity (current, quick), profitability (gross/operating/net margin, ROA, ROE),
   leverage (D/E, interest coverage), efficiency (asset/inventory/receivables turnover, **DSO / DIO
   / DPO / CCC**), and **DuPont** decomposition — all as multi-year trends, not point values.
4. **Free cash flow.** `FCF = CFO − Capex`; **FCFF** (`CFO − Capex + after-tax interest`) and
   **FCFE** (`CFO − Capex − net debt repayment`); "owner earnings" (NI + D&A − maintenance capex).
   Report the trend and FCF conversion (`FCF / Net income`).
5. **Quality of earnings.** The core forensic layer: **NI-vs-CFO gap** and its trend; the **accruals
   ratio** (`(NI − CFO) / avg total assets`); whether the gap parks in **AR** (DSO rising),
   **inventory** (DIO rising), or **capitalized costs** (PP&E/intangibles growing faster than
   sales); the **gross-margin bridge** (isolate one-off / mark-to-market noise from real operating
   movement, as with Hershey's $491M).
6. **MD&A + footnotes extraction.** Parse Item 7 (MD&A) and Item 1A (risk factors) from the 10-K
   HTML; surface cost-driver, pricing-power, commodity, and hedging language; reconcile management's
   stated "why" against what the numbers show. (LLM-assisted; keep the raw quotes with citations.)
7. **Red-flag engine.** Deterministic rules over the computed metrics: NI > CFO persistently;
   receivables/inventory outrunning revenue; margin compression; rising capitalized costs; declining
   FCF conversion; going-concern / restatement / auditor-change language. Each flag cites its
   inputs.
8. **Narrative synthesis.** LLM produces the analyst's verdict — the quality-of-earnings-adjusted
   read in plain English (the Hershey-style write-up), grounded in and citing the computed metrics
   and the MD&A quotes. Never lets the LLM invent numbers; it only narrates the computed facts.
9. **Context (optional).** Peer comparison (a small peer set: same-window ratio deltas) and
   commodity / macro overlay via **FRED** (e.g. the cocoa series `PCOCOUSDM` used to sanity-check
   Hershey's story).

## Data sources (all free, no scraping of blocked sites)

- **SEC EDGAR** (`data.sec.gov`, `www.sec.gov/Archives`) — requires a descriptive `User-Agent`
  header.
  - `https://www.sec.gov/files/company_tickers.json` — ticker → CIK map.
  - `https://data.sec.gov/submissions/CIK##########.json` — filing history; find the latest 10-K
    accession + primary document.
  - `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` — all structured financial
    facts, multi-year, as JSON (the ingestion shortcut — avoids raw XBRL for structured lines).
  - `https://www.sec.gov/Archives/edgar/data/<cik>/<accession>/<doc>.htm` — the 10-K HTML for MD&A /
    footnotes.
- **FRED** (`fred.stlouisfed.org/graph/fredgraph.csv?id=<series>`) — commodity / macro context, no
  key needed for CSV download.
- **Anthropic Claude API** — MD&A extraction + narrative synthesis (see `external/anthropic-api`).

## Proposed stack (decide at kickoff)

- **Language:** Go (matches existing skill set and `04-001`) or Python (faster for the
  data-wrangling + LLM glue). Recommendation: Python for v1 (pandas + the SEC JSON is trivial), port
  hot paths to Go later if needed.
- **Storage:** cache raw EDGAR responses on disk (they're immutable per accession); optional
  Postgres/SQLite for computed metric history (align with `04-001`'s CNPG if that exists).
- **Output:** a structured `AnalysisReport` object (JSON) + a rendered Markdown/HTML report. The
  Markdown report is the primary human artifact (tables + narrative), mirroring the tutoring
  write-up.
- **LLM boundary:** the LLM only narrates and extracts prose; **all numbers are computed
  deterministically in code** and passed to the LLM as ground truth. This keeps the analysis
  auditable.

## Phasing

- **MVP (1–2 weeks):** ticker → CIK → `companyfacts` → three statements + ratio families + FCF +
  NI-vs-CFO gap, rendered as a Markdown report. No MD&A, no LLM. Proves the ingestion + math end to
  end on Hershey and 2–3 other filers.
- **v1 (weeks):** add the quality-of-earnings layer (accruals ratio, gap-location diagnosis,
  gross-margin bridge) and the deterministic red-flag engine.
- **v2 (months):** MD&A/footnote extraction + LLM narrative synthesis; FRED commodity overlay; peer
  comparison; integration into the finance workbench.

## Integration with the finance workbench

Design the engine as a **library + CLI first**, with a thin service wrapper, so the personal-finance
workbench (`~/src/ladder`) or the portfolio dashboard (`~/src/utility/portfolio`) can call it as a
module or hit it over HTTP. Decision to make at kickoff: standalone service vs. embedded module.
Cache is shared; the workbench renders the `AnalysisReport`.

## Exit Criteria

- [ ] Given a ticker, the tool fetches the latest 10-K's data from EDGAR and builds a correct,
      multi-year Income Statement, Balance Sheet, and Cash Flow Statement (validated against the
      filing's own reported figures for ≥3 filers).
- [ ] Computes the full ratio set (liquidity, profitability, leverage, efficiency incl.
      DSO/DIO/DPO/CCC, DuPont) and free cash flow (FCFF, FCFE, owner earnings) as multi-year trends.
- [ ] Runs the quality-of-earnings checks (NI-vs-CFO gap, accruals ratio, gap-location diagnosis,
      gross-margin bridge) and emits a deterministic, citation-backed red-flag list.
- [ ] Extracts the MD&A "why" and produces a grounded plain-English verdict that cites computed
      metrics and management quotes — and never fabricates a number.
- [ ] Reproduces the manual Hershey analysis (the −14pp margin story, the $491M MTM adjustment, the
      cocoa/FRED confirmation) from a single ticker input.
- [ ] Emits a structured `AnalysisReport` (JSON) + rendered Markdown report, callable from the
      finance workbench.

## Open questions

- Go vs. Python for v1 (recommendation: Python).
- Reuse `04-001` as the ingestion layer, or build the lean `companyfacts` path here?
- Standalone service vs. embedded module in the workbench.
- How much MD&A parsing is deterministic (section splitting) vs. LLM (semantic extraction)?
- Scope of peer comparison (manual peer set vs. SIC-code auto-peers).

## Reference

- Motivating manual analysis (Hershey FY2025 + peers): financial-statements tutoring session,
  `~/src/life/financial-statements/` (study plan "Bridge" section + `sessions/`), 2026-07-02.
- Related repo projects: `04-001` (XBRL parser — ingestion), `04-005` (SEC filing sentiment — MD&A).

## Progress

- [ ] Initial research (confirm EDGAR endpoints, tag-alias coverage across filers)
- [ ] MVP (ingestion + statements + ratios + FCF + NI-vs-CFO)
- [ ] v1 (quality-of-earnings + red-flag engine)
- [ ] v2 (MD&A/LLM narrative + FRED overlay + peer comparison + workbench integration)
- [ ] Documentation
