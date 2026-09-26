# Supplementary Material — Agentic-AI Risk Taxonomy, Metrics, and Scoring Framework

Machine-readable data behind the MSc thesis *"From Risk Taxonomy to Comparable Score: A Model-Validation-Ready Framework for the Second-Line Assessment of Agentic AI in Banking"* (University of Amsterdam; research internship at ING, Model Risk
Management).

This package contains the **data artefacts** the thesis refers to as
supplementary material: the full metric register, the risk-type catalogue, the
RPN prioritisation, the theory-versus-practice comparison, and the reusable
monitoring-metric set. It is meant to be read next to the thesis, so that any
number, metric, or risk type in the text can be traced back to its source here.

A separate folder, `scoring simulation/` (the **Python code**),
reproduces the Chapter 6 scoring simulation and its figure. The two sit side by
side in the same repository.

---

## 1. What the framework is (in one minute)

The thesis builds one artefact in three layers:

1. **Taxonomy** — *what* to assess. Seven risk dimensions, 43 sub-dimensions, and
   58 risk types for agentic-AI systems in a bank.
2. **Metrics** — *how* to measure it. A register of 200 candidate metrics drawn
   from 82 sources, reduced to a small core in two parts: **Approach A** (22
   benchmark-based validation metrics, used before deployment) and **Approach B**
   (20 reusable telemetry-based monitoring metrics, used in operation).
3. **Scoring** — how to *combine* the results into one comparable, use-case-level
   risk score (with a veto floor on the critical-control dimensions).

Every file below fills in one of those layers.

The seven dimensions are: **Information Integrity, Goal Integrity, Access Control,
Action Control, Human Oversight, Monitoring & Audit, and Ecosystem Resilience.**

---

## 2. Files in this package

| File | What it is | Backs (thesis) |
|---|---|---|
| `metric_register.xlsx` | The full 200-metric register (the master file) | Ch. 4 (§4.1), Table 4.1, Appendix A.3 |
| `risk_type_catalogue.xlsx` | The 58 risk types with full definitions and candidate indicators | Appendix A.2 (Table A.2) |
| `rpn_prioritisation.xlsx` | Every risk type scored and ranked by RPN | §3.7, Appendix A.4 (funnel Stage 2) |
| `validation_vs_monitoring_metrics.xlsx` | Approach A (22) vs Approach B (20), side by side | §4.3, Table 4.2 |
| `monitoring_metrics.xlsx` | The 20 reusable monitoring metrics (Approach B), machine-readable | §4.4, Appendix B |
| `monitoring_metrics_spec/` | The same 20 monitoring metrics as a readable specification (PDF + source) | §4.4, Appendix B |

---

## 3. File-by-file guide

### `metric_register.xlsx` — the master register
The complete catalogue of candidate metrics. This is the drill-down evidence
layer behind every score in the framework.

- **`Metric Register`** — 200 metrics, one per row, each with 21 attributes:
  identity (ID, source, tier, name, definition, formula), taxonomy position
  (dimension, sub-dimension, risk type), and the measurement-character fields the
  reduction and scoring stages use (risk direction, measurement method, evidence
  required, reference dependency, measurement scale, assessment automation,
  lifecycle stage, **metric role** = capability vs risk/control, EU AI Act linkage,
  known limitation).
- **`Operational Monitoring (20)`** — the 20 Approach-B monitoring metrics.
- **`Taxonomy (Risk Types)`** — the 58 risk types (same as `risk_type_catalogue.xlsx`).
- **`Source Index`** — the 82 sources, with how many metrics each one produced.
- **`Coverage`** — metric counts per dimension, split into risk/control vs
  capability. This sheet is where the headline numbers add up (see §4 below).
- **`Column Guide`** — what each column means and why it matters for the second line.

### `risk_type_catalogue.xlsx` — the 58 risk types
One sheet (`Risk Type`), one row per risk type, five columns: dimension,
sub-dimension, risk type, a full plain-language **definition** (the wording a
validator uses to interpret the risk), and **candidate key risk indicators**.
This is the source of Appendix A.2 in the thesis.

### `rpn_prioritisation.xlsx` — risk-based prioritisation
Stage 2 of the reduction funnel. Each of the 58 risk types is scored 1–5 on four
factors — **S**everity, **O**ccurrence, agentic **A**mplification, and **D**etection
difficulty — and ranked by

```
RPN = 0.35·S + 0.25·O + 0.25·A + 0.15·D
```

- **`RPN scored (58)`** — the scored, ranked list, with a short rationale and the
  evidence per risk type.
- **`Methodology & scale`** — the formula and the 1–5 anchors for each factor.
- **`Sources`** — the evidence used for the scoring.

The RPN is a **structured prioritisation indicator**, not an estimated
probability of loss; severity is weighted highest on purpose (capability is not
the same as safety).

### `validation_vs_monitoring_metrics.xlsx` — theory meets practice
The core finding of Chapter 4: the metrics that research prioritises are not the
metrics a bank can run continuously. This workbook lays the two side by side.

- **`A - Academic + RPN`** — the 22 RPN-prioritised **validation** metrics (Approach A),
  each tied to a benchmark or paper.
- **`B - Reusability + judgement`** — the 20 reusable **monitoring** metrics (Approach B),
  each computable from live telemetry.
- **`Side-by-side`** — how each academic metric maps to its operational counterpart.
- **`Findings`** — the takeaways (why two metric sets are needed, not one).

### `monitoring_metrics.xlsx` + `monitoring_metrics_spec/` — Approach B
The 20 reusable monitoring metrics, graded by reusability tier (**R1** = directly
computable from telemetry, 17 metrics; **R2** = needs a standard probe/canary
suite, 3 metrics). About three metrics per dimension.

- `monitoring_metrics.xlsx` — the machine-readable version: ID, dimension, metric,
  purpose, formula, research basis, linkage type, required inputs, interpretation,
  and reusability tier.
- `monitoring_metrics_spec/monitoring_metrics_spec.pdf` — the same metrics as a
  readable specification (M-1.1 … M-7.3), each with its formula, research basis,
  inputs, and interpretation. `.tex` and `.bib` are the source of that PDF.

The metric IDs (M-1.1 … M-7.3) are exactly those used in the thesis Appendix B.

---

## 4. Key numbers (and how they add up)

Every figure below appears in the thesis and can be checked in the files here.

- **200** candidate metrics from **82** sources, each with **21** attributes.
- Split by role: **150 risk/control + 50 capability = 200**. The reduction funnel
  drops the 50 capability metrics first (`Coverage` sheet, `metric_register.xlsx`).
- Reference dependency: **76** reference-based + **40** reference-free + **84** rate/coverage (no reference) **= 200**.
- Assessment automation: **110** high + **48** medium + **42** low **= 200**.
- Coverage by dimension (metrics): Information Integrity 56, Goal Integrity 32,
  Access Control 28, Action Control 12, Human Oversight 15, Monitoring & Audit 34,
  Ecosystem Resilience 23.
- **58** risk types; **43** sub-dimensions; **7** dimensions.
- **Approach A** = 22 validation metrics; **Approach B** = 20 monitoring metrics
  (17 R1 + 3 R2).
- RPN weights: **0.35 / 0.25 / 0.25 / 0.15** (S / O / A / D).

Each file was checked against these figures before inclusion; they all reconcile.

---

## 5. Companion: the scoring simulation (Python)

The third layer — the comparative scoring logic — is provided as runnable code in
the companion package `scoring_simulation_reproducibility`. It regenerates the
Chapter 6 figure and every number in Section 6.2 (for example the veto floor
governing ~83% of scores) from a fixed random seed. See that package's own
`README.md`.

---

## 6. How to read this alongside the thesis

- Want the definition of a risk type? → `risk_type_catalogue.xlsx`.
- Want to see every metric and its attributes? → `metric_register.xlsx`.
- Want to know why a risk type was prioritised? → `rpn_prioritisation.xlsx`.
- Want the two-part measurement story? → `validation_vs_monitoring_metrics.xlsx`.
- Want the live monitoring metrics? → `monitoring_metrics.xlsx` + the spec PDF.

## 7. Notes

- The metrics are **design artefacts**: literature-grounded, reproducible
  measurement proposals. They have not yet been run on a live banking system;
  alert thresholds are set per use case with the second line (see the thesis
  limitations chapter).
- A few monitoring-metric sources are recent pre-prints; where a record was still
  being confirmed, this is flagged in the specification's citation note.
- Please cite the thesis when using this material.

