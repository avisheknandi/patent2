import json, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether

ROOT = os.path.join(os.path.dirname(__file__), "..")
R = json.load(open(os.path.join(ROOT, "results", "results.json")))
ss = getSampleStyleSheet()
B = ParagraphStyle("b", parent=ss["BodyText"], fontSize=8.6, leading=11)
H = ParagraphStyle("h", parent=B, fontName="Helvetica-Bold", fontSize=9.6, spaceBefore=7, spaceAfter=2)
S = ParagraphStyle("s", parent=B, fontSize=7.4, leading=9)
P = lambda t, st=B: Paragraph(t, st)

def hf(c, d):
    c.saveState(); c.setFont("Helvetica", 7.5)
    c.drawString(15*mm, 288*mm, "©VIT IPR&TT CELL"); c.drawCentredString(105*mm, 292*mm, "Invention Disclosure Format (IDF)-B")
    c.drawRightString(195*mm, 284*mm, "Doc. No. 02-IPR-R003 | Issue 2 / 01.02.2024 | Amd. 0 / 00.00.0000")
    c.drawCentredString(105*mm, 8*mm, "Page %d" % d.page); c.restoreState()

def tbl(rows, widths, head=True, fs=7.3):
    t = Table([[Paragraph(str(c), ParagraphStyle("c", parent=S, fontSize=fs, leading=fs+1.6)) for c in r] for r in rows], colWidths=widths, repeatRows=1 if head else 0)
    t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), .4, colors.grey), ("VALIGN", (0,0), (-1,-1), "TOP"),
                           ("BACKGROUND", (0,0), (-1,0 if head else -1), colors.HexColor("#e8eef5") if head else colors.white)]))
    return t

m = R["main"]; f = lambda a, n, k: m[a][n][k][0]
o, eq, cf, nv, fu = "AmI-CC (opt. budget)", "AmI-CC (equal split)", "Conformal, always full sensing", "Confidence-threshold cascade", "All sensors always (argmax)"
st = []
st += [P("1. Title of the invention", H),
       P("<b>Method and System for Energy-Optimal, Risk-Bounded Autonomous Actuation in Ambient-Intelligence IoT Using a Conformal Sensing Cascade with Optimised Risk-Budget Allocation (AmI-CC)</b>")]
st += [P("2. Field / Area of invention", H),
       P("Ambient Intelligence (AmI) for AI-native Internet of Things; context-aware multimodal sensing; energy-efficient edge AI; trustworthy (statistically guaranteed) autonomous actuation in smart homes, buildings, assisted living and Industry 5.0. (Responds to the IEEE IoT Journal special-issue CFP on \"Ambient Intelligence for AI-Native IoT: Invisible, Context-Aware, and Autonomous Experiences\": topics – AmI architectures, context-aware sensing, edge AI, explainable/trustworthy AmI, energy-efficient AI-native IoT.)")]
st += [P("3. Prior patents and publications from literature", H)]
pa = [["#", "Reference (verify before filing)", "What it teaches", "Gap vs. present invention"],
 ["1", "US 9,159,208, “Energy efficient cascade of sensors for automatic presence detection” (USPTO)", "Cascade of sensors, cheaper sensors gate costlier ones to save power.", "Gate is heuristic/threshold based; no distribution-free bound on wrong-actuation; no budget split; no deferral semantics."],
 ["2", "Angelopoulos, Bates, Fisch, Lei, Schuster, “Conformal Risk Control”, ICLR 2024 (arXiv:2208.02814)", "Calibrating a single threshold to bound expected monotone loss.", "Single model/stage; not a multi-sensor, energy-costed cascade; no allocation of a global budget across stages."],
 ["3", "“Fast yet Safe: Early-Exiting with Risk Control”, arXiv:2405.20915", "Risk-controlled early exit in neural networks.", "Exits inside one network (compute saving); does not power physical sensor tiers, no energy-optimal per-tier budget split, no actuate/escalate/defer policy."],
 ["4", "“Efficient Conformal Prediction via Cascaded Inference with Expanded Admission”, arXiv:2007.03114", "Cascaded models to cheapen conformal sets.", "Model cascade for set size; no sensing-hardware wake-up, no actuation risk."],
 ["5", "Gibbs & Candès, “Adaptive Conformal Inference Under Distribution Shift”, NeurIPS 2021", "Online adaptation of miscoverage level under shift.", "Generic; not applied to per-tier budgets of a sensing cascade."],
 ["6", "Jitkrittum et al., “When Does Confidence-Based Cascade Deferral Suffice?”, NeurIPS 2023 (arXiv:2307.02764)", "Analysis of confidence-threshold deferral in model cascades.", "Heuristic confidence rules, no finite-sample guarantee (our baseline behaves this way)."],
 ["7", "“Sensor-Aware Classifiers for Energy-Efficient Time Series Applications on IoT Devices”, arXiv:2407.08715", "Early-exit classifiers exploiting sensor structure for energy.", "No statistical guarantee on wrong decisions; no joint budget allocation."],
 ["8", "“Early Time Classification with Accumulated Accuracy Gap Control”, arXiv:2402.00857", "Stopping-time classification with accuracy-gap control.", "Time-series stopping, not multi-tier hardware sensing, no energy-optimal allocation."]]
st += [tbl(pa, [7*mm, 52*mm, 48*mm, 73*mm]), P("Note: a professional patent-database search (Espacenet/Google Patents/InPASS, CPC G06N 20/00, G16Y, H04W 52/02, G05B 13) must confirm this table before filing. References 1–8 were identified by web search on 30-Sep-2026; only titles/abstract-level content was reviewed.", S)]
st += [P("4. Summary and background of the invention (gap / novelty)", H),
 P("<b>Background.</b> Ambient IoT must act <i>invisibly</i> (no user prompts), yet a wrong autonomous action (unlocking a door, switching a heater, dismissing a fall alert) is costly, while always-on rich sensors (camera, mmWave radar) drain batteries and raise privacy exposure. Existing systems either (a) run all sensors and a single classifier (high energy, and softmax confidence is uncalibrated), or (b) use heuristic confidence-threshold sensor cascades that give no assurance on how often they act wrongly, especially for unseen occupants."),
 P("<b>Gap.</b> No known system couples a <i>physical sensing-tier wake-up cascade</i> with a <i>finite-sample, distribution-free bound on wrong autonomous actuation</i> while <i>choosing how that bound is spent across tiers to minimise energy</i>."),
 P("<b>Invention.</b> At each tier a split-conformal prediction set over candidate intents is computed. A singleton set triggers actuation and stops (higher-energy sensors stay asleep); a non-singleton set wakes the next tier; ambiguity at the last tier defers to the user (or a safe default). A wrong actuation implies the true intent was outside the stopping tier's set, so the wrong-actuation probability is bounded by the sum of per-tier miscoverage levels (union bound) – the <b>risk budget α</b>. The novel <b>budget-allocation step</b> searches the split of α over tiers that minimises expected energy + λ·deferral-rate on one data split, and calibrates the thresholds on a <i>disjoint</i> split, so the guarantee stays valid. On-site recalibration with few labelled samples restores the bound under occupant shift.")]
st += [P("5. Objective(s) of the invention", H),
 P("(i) Bound the rate of erroneous autonomous actuation by a user/operator-set budget α without distributional assumptions; (ii) minimise sensing energy by waking high-power / privacy-intrusive modalities only when cheaper ones are ambiguous; (iii) provide a principled abstain (“ask user”) behaviour instead of forced decisions; (iv) make the guarantee portable to new occupants/homes through lightweight recalibration; (v) run on edge hardware (logistic/linear heads suffice; cost of allocation is a small grid search).")]
st += [P("6. Working principle (in brief)", H),
 P("Tier-t score s=1−p<sub>t</sub>(y|x); threshold q<sub>t</sub> = ceil((n+1)(1−α<sub>t</sub>))-th smallest calibration score; set C<sub>t</sub>(x)={k: 1−p<sub>t,k</sub>(x) ≤ q<sub>t</sub>}. Rule: |C<sub>t</sub>|=1 → actuate &amp; stop; else escalate; last tier non-singleton → defer. P(wrong actuation) ≤ Σα<sub>t</sub> ≤ α. Allocation: (α<sub>1..T</sub>)* = argmin E[energy]+λP(defer) s.t. Σα<sub>t</sub>≤α (grid search on allocation split), thresholds from a disjoint calibration split.")]
st += [P("7. Description of the invention in detail", H),
 P("<b>7.1 Architecture.</b> (a) Sensing tiers T1 passive low-power (PIR, door contact, ambient light, time-of-day; 1 energy unit), T2 medium (plug power, audio level, BLE RSSI; 6 units), T3 high (camera / mmWave embedding; 40 units); (b) per-tier classifiers over cumulative features (edge MCU / gateway); (c) conformal calibrator storing per-tier score quantiles; (d) budget allocator; (e) actuation controller with escalate / actuate / defer outputs; (f) optional on-site recalibration module fed by user overrides."),
 P("<b>7.2 Procedure.</b> <i>Offline:</i> 1) train tier classifiers on training occupants; 2) on allocation split run the cascade for each candidate split (α<sub>1</sub>,…,α<sub>T</sub>) with Σ=α and keep the split minimising J=E[cumulative energy]+λ·P(defer); 3) on a disjoint calibration split compute q<sub>t</sub>. <i>Online:</i> power tier 1, compute set; if singleton → actuate; else power tier 2 … ; at the last tier defer if not singleton."),
 P("<b>7.3 Why the bound holds.</b> If the cascade actuates wrongly at tier t then C<sub>t</sub>={ŷ} with ŷ≠y, hence y∉C<sub>t</sub>; split-conformal gives P(y∉C<sub>t</sub>)≤α<sub>t</sub> under exchangeability; union over tiers gives ≤Σα<sub>t</sub>. Because the allocation uses data disjoint from the calibration data, the q<sub>t</sub> remain valid."),
 P("<b>7.4 Implementation.</b> Reference implementation in Python (repository: <i>amicg/</i>: simulator.py, cascade.py; experiments/run_experiments.py; tests/test_cascade.py, unit tests pass). Drawing (block diagram):", B)]
dia = [["Sensors T1 (1u)", "→", "Classifier<sub>1</sub> + conformal set C<sub>1</sub>", "→", "|C<sub>1</sub>|=1 ?  yes → ACTUATE (stop)"],
       ["", "", "no ↓ wake T2 (6u)", "", ""],
       ["Sensors T2 (+6u)", "→", "Classifier<sub>2</sub> + set C<sub>2</sub>", "→", "|C<sub>2</sub>|=1 ? yes → ACTUATE"],
       ["", "", "no ↓ wake T3 (40u)", "", ""],
       ["Sensors T3 (+40u)", "→", "Classifier<sub>3</sub> + set C<sub>3</sub>", "→", "|C<sub>3</sub>|=1 ? yes → ACTUATE ; no → DEFER to user"]]
st += [tbl(dia, [35*mm, 8*mm, 55*mm, 8*mm, 70*mm], head=False, fs=7.6),
       P("Fig. 1 – Conformal sensing cascade. Budget allocator chooses α<sub>1</sub>+α<sub>2</sub>+α<sub>3</sub> ≤ α; wrong actuation ≤ α.", S)]
st += [P("8. Experimental validation results", H),
 P("<b>Setup (simulation; no real-deployment data yet).</b> Synthetic multi-tier smart-home benchmark with 8 intents (idle, enter home, cooking, TV, sleep, leave, exercise, fall-risk), 3 cumulative sensing tiers (6/14/26 features, energy 1/6/40 units), per-occupant offsets (inter-occupant covariate shift) and deliberately confusable intent pairs at low tiers. Per seed: 24 training occupants, 10 allocation, 14 calibration, 24 unseen test occupants × 150 samples; 30 random seeds; mean values shown. Tier accuracies (single seed): T1 67%, T2 80%, T3 99.6%. Baselines: always-all-sensors argmax; tier-1 only; single-stage conformal with always-full sensing; confidence-threshold cascade (single threshold tuned on the same calibration split to hit α, forced decision at last tier); ablation: equal budget split.")]
rows = [["α", "Method", "False-actuation rate", "Energy / decision", "Deferral rate", "Seeds with FA>α"]]
for a in ["0.01", "0.02", "0.05", "0.1"]:
    for n, lab in [(o, "AmI-CC (proposed)"), (eq, "AmI-CC, equal split"), (cf, "Conformal, full sensing"), (nv, "Conf.-threshold cascade"), (fu, "All sensors, argmax")]:
        rows.append([a, lab, "%.4f" % f(a, n, "false_act"), "%.1f" % f(a, n, "energy"), "%.3f" % f(a, n, "defer"), "%.0f%%" % (100*m[a][n]["viol_rate"])])
st += [tbl(rows, [12*mm, 42*mm, 34*mm, 30*mm, 28*mm, 30*mm]), P("Table 1 – mean over 30 seeds (std. in results/results.json). Tier-1-only: FA=0.330, energy 1.", S)]
e5 = f("0.05", o, "energy"); sv = 100*(1-e5/47)
st += [P("<b>Findings.</b> (1) The mean false-actuation rate of AmI-CC is below the budget for every α (e.g. %.3f at α=0.05; %.3f at α=0.10), as the bound predicts (per-seed violations, 7–17%%, are finite-sample fluctuation of a bound that holds in expectation). (2) At α=0.05 AmI-CC uses %.1f energy units vs 47.0 for always-full sensing: <b>%.0f%% saving</b> (63%% at α=0.10: 17.6 vs 47.0) with FA %.3f vs %.4f for the full-sensing argmax at its fixed operating point – i.e. the operator trades risk for energy in a controlled, tunable way. (3) Budget optimisation reduces energy by %.0f%% vs equal split at α=0.05 (%.1f vs %.1f) and allocates almost all the budget to tier 2 (mean split α<sub>1</sub>/α<sub>2</sub>/α<sub>3</sub> = %s). (4) The tuned confidence-threshold cascade reaches similar mean energy (%.1f) but has no guarantee: it exceeds α in 47%% of seeds at α=0.05 (40–57%% across α) versus 10%% for AmI-CC, and cannot defer. <b>Honest limitation:</b> energy is on par with that heuristic baseline, the benefit is the guarantee and the defer option." % (f("0.05", o, "false_act"), f("0.1", o, "false_act"), e5, sv, f("0.05", o, "false_act"), f("0.05", fu, "false_act"), 100*(1-e5/f("0.05", eq, "energy")), e5, f("0.05", eq, "energy"), [round(x, 3) for x in R["alloc"]["0.05"]], f("0.05", nv, "energy")))]
sh = [["Occupant-shift severity", "FA, calibrated pre-deployment", "FA, + on-site recalibration (800 labelled)", "Deferral after recalibration"]]
for s in ["1.0", "1.5", "2.0", "3.0"]:
    sh.append(["×" + s, "%.3f" % R["shift"][s][o]["false_act"][0], "%.3f" % R["recal"][s][o]["false_act"][0], "%.2f" % R["recal"][s][o]["defer"][0]])
st += [P("<b>Robustness to occupant shift (α=0.05).</b> The exchangeability assumption fails when test occupants are more heterogeneous than calibration occupants: the bound is exceeded (Table 2). On-site recalibration with 800 labelled samples from the new environment restores it, paying with more deferrals/energy (the system safely asks more)."),
       tbl(sh, [40*mm, 45*mm, 55*mm, 40*mm]), P("Table 2.", S)]
st += [KeepTogether([Image(os.path.join(ROOT, "results", "fig_main.png"), width=175*mm, height=48.5*mm), P("Fig. 2 – Risk-budget sweep: false-actuation, energy, deferral (30 seeds).", S)]),
       KeepTogether([Image(os.path.join(ROOT, "results", "fig_shift.png"), width=85*mm, height=58*mm), P("Fig. 3 – Effect of occupant shift with/without recalibration.", S)]),
       P("Reproduce: <font face='Courier'>python experiments/run_experiments.py; python experiments/make_figures.py; python tests/test_cascade.py</font>. <b>Status:</b> results are from a simulator, not field data; a pilot on a public smart-home dataset / campus testbed is planned before TRL≥4 claims and is recommended before the IoTJ submission.", S)]
st += [P("9. What aspect(s) need protection?", H),
 P("<b>Independent claim 1 (method):</b> controlling actuation in an ambient IoT system comprising: powering a first sensing tier; computing with a first classifier a conformal prediction set of candidate intents whose threshold is calibrated to a first miscoverage level α<sub>1</sub>; actuating if the set is a singleton and otherwise powering a higher-energy tier and repeating; deferring if the last-tier set is not a singleton; wherein the miscoverage levels satisfy Σα<sub>t</sub> ≤ α, a predetermined actuation-risk budget, and are selected by minimising an objective comprising expected sensing energy on a data split disjoint from the split used to calibrate the thresholds."),
 P("<b>Dependent aspects:</b> (2) objective includes deferral (user-interruption) cost λ; (3) grid/convex search of the allocation; (4) per-tier classifiers on cumulative features; (5) on-site recalibration from user overrides when a drift detector fires, raising deferral to preserve the bound; (6) tiers including PIR/door/light → plug-power/audio/BLE → camera/mmWave, so privacy-intrusive sensors are powered only on ambiguity; (7) class-conditional (per-action criticality) budgets [not yet validated]; (8) system, and (9) non-transitory medium claims. <i>Technical effect emphasised for eligibility (e.g. Indian Patents Act s.3(k) / 35 USC §101): reduced power consumption of sensor hardware and a bounded rate of erroneous physical actuation.</i>")]
st += [KeepTogether([P("10. Technology readiness level", H),
 tbl([["TRL 1", "TRL 2", "TRL 3", "TRL 4", "TRL 5", "TRL 6", "TRL 7", "TRL 8", "TRL 9"],
      ["Basic principles observed", "Concept formulated", "[X] Experimental proof of concept (simulation, this work)", "Validated in lab (planned: testbed)", "Relevant environment", "Demonstrated in relevant env.", "Prototype in operational env.", "System complete & qualified", "Proven in operational env."]],
     [19*mm]*9, fs=6.6),
 P("Ticked: <b>TRL 3</b> (experimental proof of concept). Target: TRL 4 after a lab testbed run.", S)]), Spacer(1, 6), P("---------------------- END OF THE DOCUMENT -----------------------------", S)]
SimpleDocTemplate(os.path.join(ROOT, "Invention_Disclosure_Format_B_FILLED.pdf"), pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=18*mm, bottomMargin=14*mm,
                  title="IDF-B: AmI-CC", author="Inventor(s) – to be completed").build(st, onFirstPage=hf, onLaterPages=hf)
