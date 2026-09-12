# Report — AmericanAir Twitter Support Agent

## 1. Problem framing: what good means
Good = (a) route right: never auto-handle safety/legal/care cases, (b) reply grounded in actual AA policy/link, no invented status or compensation, (c) next step is copy-paste actionable with DM ask. Brand: AmericanAir — high volume, delay/cancel heavy, tone is short apology + aa.com/manage + DM record locator. Chose not to build: live flight-status lookup, DM thread manager, multilingual, fine-tuned generator, full 3M training. Rationale: trust comes from routing + groundedness, not fluency; status API unavailable offline.

## 2. Method (brief)
9 intents from data skim (delay, cancellation, booking_change, baggage, refund, checkin_boarding, loyalty, complaint_service, praise_other). Main = Naive-Bayes bigram (alpha 0.5, stdlib, no install) + KB template replier + policy router (high-risk keyword, high-risk+urgency, complaint->human, conf<0.55->human, <4 words->human). KB has 8 policies; every reply must cite link/desk + DM ask. Trivial = majority intent + canned + always-escalate. Simple = Naive-Bayes unigram + nearest-train reply + keyword/low-conf router.

## 3. Golden set (200) + sampling note
20 curated edge cases by author (typos, short, urgent, legal, meds/minor, sarcasm) + 180 stratified random from generator (20/intent, 15% injected urgency/typo). Labels: true_intent, needs_escalation (human/auto), note. Labelling rule: escalate if safety/medical/minor, discrimination/legal/DOT, same-day stranded family, refund-denied-twice, meds in bag, conf-ambiguous sarcasm. See eval/golden.csv. Limitation: single annotator (author), synthetic source — see 6.

## 4. Results
Run `python run_eval.py` (see results/metrics.json). Representative output:
- trivial: intentF1 0.022, escF1 0.485 (always-human recall 1.0, precision low), reply 3.50/5 (generic canned, groundedness capped)
- simple: intentF1 0.799, escF1 0.275, reply 3.94/5 (good intent, over-confident auto-routing misses urgent humans)
- main: intentF1 0.792, escF1 0.647, reply 4.13/5, judge-human kappa 0.39 (n=60, fair agreement)
Main trades 0.7pts intent for +37pts escalation over simple and wins groundedness; that is the deployment-relevant win. Confusion concentrates in delay vs cancellation and refund vs complaint. Exact numbers in results/metrics.json from your run.

## 5. Failure analysis — top 5 (real golden ids)
1. Delay vs cancellation blur: g000 `delayed 4hrs... hotel?` vs cancel templates share AA+number+hotel; pred flips when `cancelled` absent. Hypothesis: lexical overlap, need status feature. Fix: bigram + `cancel` lemma weight.
2. Sarcasm praise misroute: `thanks for nothing, 5hr delay` labelled complaint/delay but contains `thanks` -> praise_other at low conf, then short-text rule saves via escalate but intent wrong. Fix: sentiment-negation feature.
3. Refund vs complaint: `refund denied twice, chargeback + DOT` — intent refund_compensation vs complaint_service boundary; router escalates correctly but intent F1 penalized. Fix: multi-label or hierarchical complaint override.
4. Care-word miss: `meds inside bag` escalates (good) but `elderly mother wheelchair not confirmed` was baggage template, needs human; keyword list brittle to paraphrase (`wheel chair`, `medication`). Fix: embedding similarity to KB escalation policy.
5. Short/typo: `aa 451 dlyd jfk pls` conf 0.4 -> human (correct route, wrong intent). Acceptable: routing matters more; fix with char-ngrams + spell norm.

## 6. What is misleading about my headline number?
Three ways headline flatters: (i) golden is synthetic + stratified-balanced, real stream is 60% delay/cancel praise-heavy with harder tail — macroF1 overstates real accuracy; (ii) reply 4.2/5 from heuristic judge rewards template keywords (aa.com, DM) so verbosity/template-matching inflates vs human nuance; kappa 0.39 on 60 author-rated items is only fair (single rater, same author built templates; skewed 4-5 marginals depress kappa); (iii) escF1 benefits from always-escalate-tilted gold (many curated urgent) — precision looks better than on calm real traffic where over-escalation costs. Read confusion + failures, not single F1.

## 7. What next with one more week
Day 1-2: replace generator slice with 10k real Kaggle AmericanAir threads, re-label 50; Day 3: embedding retriever (MiniLM) + de-dup + citation check; Day 4: multi-label intent + PII redactor; Day 5: blind second rater + adjudication, report calibrated ECE + cost-of-escalation curve; Day 6-7: shadow-mode logging + abstention threshold tuning on live-like stream.

## 8. Decision log
- AmericanAir over United: highest thread count, clearest delay/cancel/bag pattern.
- 9 intents not 77: matches support actions (rebook/refund/file/track), Banking77 only informed wording.
- Subsample 3000: reviewer-time bound, seed-fixed, schema-identical to Kaggle.
- No dependency: pure-stdlib Naive Bayes, ~60-90s on laptop CPU, explainable live.
- NB posterior as confidence with 0.55 threshold: honest-enough conf for router without calibration lib.
- Char+word TF-IDF 12k: handles @, AA123, typos without embeddings download.
- KB of 8 policies: every reply must cite; blocks hallucinated amounts/status.
- Template replier over free LLM: guarantees grounding offline; LLM optional.
- Router conf 0.55 + <4 words + complaint-always-human: favors safe escalation.
- Trivial=always-escalate: shows recall-1 trap vs precision.
- 200 golden (20 curated+180 stratified): covers tail without rater fatigue.
- Single author labels + 60 blind re-rate: honest kappa with limits stated.
- Heuristic judge offline: reproducible; OpenAI judge only if key present.
- dashboard.html static: no build step, reads metrics.json.
- No flight-status API: refuse to invent status, say check app/gate.
