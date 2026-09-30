# AmI-CC – Conformal Sensing Cascade for Ambient IoT

Patent idea for the IEEE IoT Journal CFP *Ambient Intelligence for AI-Native IoT*: energy-optimal, risk-bounded autonomous actuation.
Tiered sensors wake only when the conformal prediction set is ambiguous; the actuation-risk budget α is split across tiers to minimise energy; ambiguity at the last tier defers to the user.

* `amicg/` – implementation (simulator, cascade, allocation, calibration)
* `experiments/` – `run_experiments.py` (30 seeds, ≈5 min), `make_figures.py`
* `tests/test_cascade.py` – unit tests
* `results/` – `results.json`, figures
* `Invention_Disclosure_Format_B_FILLED.pdf` – completed IDF-B (rebuild: `python docs/build_idf.py`)
* `docs/PATENT_ROADMAP.md` – claims, novelty analysis, filing → publication → grant plan

Requires numpy, scikit-learn, matplotlib, reportlab, pymupdf. **Results are from a simulator; real-data validation is still to do.**
