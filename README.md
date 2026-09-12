# Hiver SDE Intern — AmericanAir Support Agent

One-brand AI support agent on Twitter-style conversations. For each incoming customer message it: (1) classifies intent into 9 intents defined from the data, (2) drafts a reply grounded in how AmericanAir historically resolved similar issues (8-policy knowledge base), (3) decides auto-handle vs escalate-to-human with a stated reason. The proof (golden set + harness + judge agreement + failure analysis) matters more than the bot.

## Starting command (one line)

```
python run_eval.py
```

That is the whole backend: trains trivial + simple + main, evaluates on the 200-item golden set, prints the HEADLINE, writes `results/metrics.json`.

## Backend + UI in one line

There is no backend server to keep alive. The UI is a static page that reads `results/metrics.json`.

```
python run_eval.py; python -m http.server 8000
```

Then open `http://localhost:8000/dashboard.html`. If you just double-click `dashboard.html` without the server, browsers may block `fetch()` of the JSON — use the server line above.

## Reproduce headline results in under 15 minutes

1. `python --version` — need 3.10+.
2. `python run_eval.py` — stdlib only, no `pip install`, works offline, ~1–2 min.
3. Read the last console line, e.g. `HEADLINE: main intentF1=0.792 escF1=0.647 reply=4.13/5 kappa=0.391`.
4. Open `results/metrics.json` for full numbers, `eval/human_judge_sample.csv` for the 60-item judge-vs-human sample.

Optional: with an OpenAI key, `pip install openai` and set `OPENAI_API_KEY` before rerunning — a `gpt-4o-mini` judge score is logged under `llm` next to the offline heuristic. Not required.

## Headline results (from this repo)

| model | intent macro-F1 | intent acc | escalation F1 | reply overall /5 |
|---|---|---|---|---|
| trivial (majority + canned + always-escalate) | 0.022 | 0.11 | 0.485 | 3.50 |
| simple (NB-unigram + nearest-reply) | 0.799 | 0.805 | 0.275 | 3.94 |
| main (NB-bigram + KB-grounded + policy-router) | 0.792 | 0.79 | 0.647 | 4.13 |

Judge–human agreement: Cohen kappa 0.391, n=60 (fair; single author-rater, 4–5 skewed marginals — see REPORT section 6).

Reading: main trades 0.7 pts of intent F1 vs simple for +37 pts of escalation F1 and the most grounded replies. That trade is the deployment-relevant win.

## What is here

- `run_eval.py` — the harness: trains, evaluates intent acc/F1, escalation P/R/F1, reply 1–5, kappa, failures, confusion matrix.
- `src/intents.py` — 9 intents + risk levels + escalate/urgent keywords.
- `src/make_data.py` — deterministic subsample generator (3,000 threads, seed 42) mirroring the Kaggle schema.
- `src/make_golden.py` — golden-200 builder: 20 curated edge cases + 180 stratified (~22/intent, typos/urgent mix, seed 7).
- `src/baselines.py` — trivial and simple baselines.
- `src/agent.py` — main agent: NB-bigram + KB-grounded templates + confidence + policy router.
- `src/judge.py` — reply judge: groundedness / actionability / tone / safety, 1–5 each, overall = mean.
- `src/textutils.py` — stdlib tokenizer + Naive Bayes + PRF + kappa (no sklearn needed).
- `data/threads_sample.csv` — training subsample (thread_id, intent, inbound, brand_reply).
- `data/knowledge_base.json` — 8 AmericanAir policies every reply must ground in.
- `eval/golden.csv` — id, text, true_intent, needs_escalation, suggested_action, label_note.
- `eval/rubric.md` — the 1–5 rubric.
- `eval/human_judge_sample.csv` — 60 blind re-rates for judge agreement.
- `results/metrics.json` — full output (per-model metrics, judges, failures, confusion matrix).
- `REPORT.md` — framing, method, golden note, results, top-5 failures, misleading-number section, next week, 15-point decision log.
- `dashboard.html` — static results viewer (no build step).

## Intents (9)

`flight_delay`, `cancellation`, `booking_change`, `baggage`, `refund_compensation`, `checkin_boarding`, `loyalty_account`, `complaint_service`, `praise_other`. High-risk (always lean human on urgency): cancellation, refund_compensation, complaint_service. Full definitions in `src/intents.py`.

## Data note (why synthetic subsample)

The full Kaggle `thoughtvector/customer-support-on-twitter` (~3M tweets) is not run here — by design, per the brief (“a subsample is expected”). `src/make_data.py` mirrors its schema and AmericanAir voice/links so the pipeline runs offline in ~2 min. To run on real data: download the Kaggle CSV, filter AmericanAir threads, map columns to thread_id/inbound/brand_reply/intent, drop into `data/threads_sample.csv`, rerun `python run_eval.py`. Golden sampling/label rules are in `REPORT.md` section 3.

## Troubleshooting

- `No output yet` — the pure-Python NB pass takes 60–90 s; wait for the HEADLINE line.
- `Dashboard shows old numbers` — rerun `python run_eval.py` first; the page reads `results/metrics.json` fresh each load (hard-refresh).
- `fetch failed on file://` — serve via `python -m http.server 8000`, do not double-click the HTML.
- `Fresh start` — delete `data/threads_sample.csv` + `eval/golden.csv` and rerun; both regenerate deterministically.
