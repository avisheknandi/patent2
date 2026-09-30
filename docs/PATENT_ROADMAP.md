# AmI-CC: path to publication and grant

**No one can guarantee grant.** This plan maximises the chance and sequences the steps so the invention is not lost to its own publication.

## 1. Why this idea is patentable (and where it is weak)
| Criterion | Position | Risk |
|---|---|---|
| Eligibility (India s.3(k); US §101) | Claim a *sensor-hardware control method*: staged power-up of physical sensors and bounded physical actuation, with measured energy saving. Do not claim "an algorithm" alone. | Medium – keep the claims anchored to sensors, wake-up and actuator. |
| Novelty (s.102 / Indian s.2(1)(j)) | No reference found combining conformal sets + sensor tiers + energy-optimal split of the error budget. | Needs a professional search (see IDF table; US 9,159,208 and arXiv:2405.20915 are closest). |
| Inventive step / non-obviousness | Budget *allocation on a split disjoint from calibration* yields both validity and a 17% energy reduction vs equal split; heuristic cascade offers no guarantee (47% of seeds exceed α). | Medium – examiner may combine sensor cascades with conformal risk control. Dependent claims (deferral cost λ, recalibration trigger, privacy-ordered tiers) are fallback positions. |
| Industrial applicability | Smart home, assisted living, industry. | Low. |
| Enablement | Code + equations + parameters in repo and IDF. | Low. |

## 2. Sequence (do not break the order)
1. **Now – internal:** submit `Invention_Disclosure_Format_B_FILLED.pdf` to the VIT IPR&TT Cell. Add inventor names, affiliations, and declarations (left blank).
2. **Before ANY public disclosure (arXiv, talk, IoTJ submission):** file a provisional (US/IN) or Indian complete-with-provisional. Publishing first forfeits absolute-novelty jurisdictions (India, EP, CN).
3. **Professional prior-art search** + claim refinement (attorney). Ask for a freedom-to-operate check on US 9,159,208 family.
4. **Strengthen evidence before the complete specification (≤12 months):** (a) run on a real public smart-home/HAR dataset and a small hardware testbed (measure real mJ on a low-power MCU + camera/radar module); (b) add per-action-criticality (Mondrian) budgets and validate claim 7; (c) add ablations (single-tier conformal, other score functions).
5. **Complete filing + PCT (month 12):** India request for examination (Form 18/18A – expedited for startups/educational institutions), PCT if abroad protection wanted.
6. **Publication:** Indian applications publish ~18 months from priority (early publication on request, Form 9, is possible). Then examination → First Examination Report → respond (typically 6 months) → grant. Budget 2–4 years overall.
7. **Paper (IEEE IoT Journal special issue on Ambient Intelligence):** submission deadline **15 Feb 2027**, first review 30 Apr 2027, final manuscript 15 Aug 2027, publication Oct 2027. Submit **after** step 2. The journal paper should use real-data results from step 4.

## 3. Draft claims
1. A method of controlling actuation in an ambient IoT system, comprising: (a) activating a first sensing tier of T ordered tiers of increasing energy cost; (b) computing, by a classifier for said tier, a prediction set of candidate user intents that contains the true intent with probability ≥ 1−α_t, the set threshold being calibrated on calibration data; (c) when the set has a single element, actuating the corresponding action and leaving higher tiers inactive; (d) otherwise activating the next tier and repeating (b)–(c); (e) when the set at the last tier has more than one element or is empty, deferring the decision to a user or safe default; wherein Σα_t ≤ α, a predetermined actuation-risk budget, and the α_t are selected by minimising an objective that includes expected sensing energy, evaluated on data disjoint from the calibration data.
2. …wherein the objective further includes λ × probability of deferral.
3. …wherein selection is an exhaustive search over a grid of budget splits.
4. …wherein tier t's classifier receives features of tiers 1..t.
5. …further comprising recalibrating the thresholds from user-override labels collected on site when a drift detector signals, deferring more often in the interim.
6. …wherein tier 1 comprises PIR/door/light/time sensors, tier 2 plug-power/audio-level/BLE-RSSI, tier 3 camera or mmWave radar.
7. A system comprising sensors, a processor and memory implementing claim 1. 8. A non-transitory medium storing instructions for claim 1.

## 4. Open items (need the inventors)
Inventor names/affiliations/signatures; real-data pilot; attorney search; decision on jurisdictions; funding-agency/ institutional disclosure obligations.

## 5. Making the validation real (before signing the declaration or raising the TRL)
1. Run `python tests/test_cascade.py` and `python experiments/run_experiments.py`; read `amicg/cascade.py` until you can explain every step and change something yourself.
2. Replace the simulator with a public activity/smart-home dataset, using subject-wise splits (calibrate on some people, test on others) with the same three feature tiers.
3. Measure energy on hardware: a low-power MCU with a PIR/light sensor, a mid-tier sensor and a camera or mmWave module. Log mJ per wake-up and replace the 1/6/40 units with measured values.
4. Re-report the same tables. Only then consider TRL 4 and update Section 8, the TRL tick and the declaration.
