# Agentic AI — a model-validation-ready risk taxonomy, metrics, and scoring framework

![Reproduce](https://github.com/ducquanng/agentic-ai-risk-scoring/actions/workflows/reproduce.yml/badge.svg)
 
Supplementary material and reproducibility code for the MSc thesis
 
> **From Risk Taxonomy to Comparable Score: A Model-Validation-Ready Framework for the Second-Line Assessment of Agentic AI in Banking**
> Duc Quan Nguyen — MSc Data Science and Business Analytics, University of Amsterdam.
> Written during a research internship at ING, Model Risk Management.
 
This repository holds the two artefacts the thesis refers to as supplementary material: the **machine-readable data** behind the taxonomy and metrics, and the **runnable code** that reproduces the Chapter 6 scoring simulation. Everything here is meant to be read next to the thesis, so any number, metric, or risk type in the text can be traced back to its source.
 
---
 
## What the framework is (in one minute)
 
The thesis builds one artefact in three layers:
 
1. **Taxonomy** — *what* to assess. Seven risk dimensions, 43 sub-dimensions, and 58 risk types for agentic-AI systems in a bank.
2. **Metrics** — *how* to measure it. A register of 200 candidate metrics from 82 sources, reduced to a small core in two parts: **Approach A** (22 benchmark-based validation metrics, used before deployment) and **Approach B** (20 reusable telemetry-based monitoring metrics, used in operation).
3. **Scoring** — how to *combine* the results into one comparable, use-case-level risk score, with a **veto floor** on the three critical-control dimensions (Access Control, Action Control, Monitoring & Audit).
The seven dimensions are: **Information Integrity, Goal Integrity, Access Control, Action Control, Human Oversight, Monitoring & Audit, and Ecosystem Resilience.**
 
---
 
## Repository layout
 
| Folder | What it is | Start here |
|---|---|---|
| `supplementary material/` | The machine-readable data artefacts — the 200-metric register, the 58-risk-type catalogue, the RPN prioritisation, the theory-vs-practice comparison, and the 20 reusable monitoring metrics (with a readable spec). | its own `README.md` |
| `scoring simulation/` | The Python package that reproduces the Chapter 6 Monte-Carlo study and its figure, from a fixed random seed. | its own `README.md` |
 
Each folder has its own detailed README; this page is the overview that ties them together.
 
---
 
## Quick start — reproduce the Chapter 6 numbers
 
```bash
cd "scoring simulation"
pip install -r requirements.txt
python scoring_simulation.py
```
 
This runs in well under a minute on a laptop and needs only `numpy`, `scipy`, and `matplotlib`. It writes:
 
- `outputs/section_6_2_numbers.csv` — every figure quoted in Section 6.2, next to the value the code actually computed (so each is traceable).
- `outputs/sim_scoring.png` — the three-panel figure from the thesis.
- seven more CSVs — the Sobol' indices, robustness checks, and ablations behind the chapter.
The run is fully deterministic (`SEED = 20260713`); re-running reproduces the same numbers byte-for-byte. A GitHub Actions job reruns the study on a clean machine on every push and monthly, and fails if any committed CSV differs by a byte — the badge above is that check. The numbers were last confirmed under NumPy 2.4 / SciPy 1.17, four library generations after they were produced; the figure is excluded from the comparison because Matplotlib's PNG output depends on its own version and the fonts installed. A ready-to-run `scoring_simulation.ipynb` notebook is provided as well (regenerate it from the script with `python build_notebook.py`).
 
---
 
## Key numbers (and where they live)
 
Every figure below appears in the thesis and can be checked in the files here.
 
- **200** candidate metrics from **82** sources; **150** risk/control + **50** capability = 200.
- **58** risk types; **43** sub-dimensions; **7** dimensions.
- **Approach A** = 22 validation metrics; **Approach B** = 20 monitoring metrics (17 directly reusable + 3 via a probe/canary suite).
- RPN weights **0.35 / 0.25 / 0.25 / 0.15** (Severity / Occurrence / Amplification / Detection).
- In simulation: the veto floor is the binding term in **~82.5%** of random systems, and the three critical-control dimensions carry **~93%** of the score's variance (Sobol' total-effect share).
---
 
## How this maps to the thesis
 
- Want the definition of a risk type? → `supplementary material/` → `risk_type_catalogue.xlsx` (thesis Appendix A.2).
- Want every metric and its attributes? → `supplementary material/` → `metric_register.xlsx` (thesis Chapter 4).
- Want to see how a bank's runnable metrics differ from the research-prioritised ones? → `validation_vs_monitoring_metrics.xlsx` (thesis Chapter 4/5).
- Want to reproduce the scoring behaviour and the Chapter 6 figure? → `scoring simulation/`.
---
 
## Notes
 
- The metrics and thresholds are **design artefacts**: literature-grounded, reproducible measurement proposals. They have not yet been run on a live banking system; thresholds are set per use case with the second line (see the thesis limitations chapter).
- The scoring study is a **structural/behavioural analysis of the aggregation operator** — it establishes properties of the formula under stated assumptions, not risk levels of real deployed systems.
## Citation
 
If you use this material, please cite the thesis:
 
> Nguyen, D. Q. (2026). *From Risk Taxonomy to Comparable Score: A Model-Validation-Ready Framework for the Second-Line Assessment of Agentic AI in Banking.* MSc thesis, University of Amsterdam.
 
