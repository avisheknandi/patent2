import json, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from amicg import SmartHomeSimulator, ConformalCascade, TIER_ENERGY
from amicg.cascade import conformal_q

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
N_SEEDS = 30
ALPHAS = [0.01, 0.02, 0.05, 0.10]
LAM = 20.0


def metrics(y, act, energy, stop=None):
    actuated = act >= 0
    wrong = actuated & (act != y)
    return dict(false_act=wrong.mean(), act_rate=actuated.mean(), defer=1 - actuated.mean(),
                sel_err=(wrong.sum() / max(1, actuated.sum())), energy=energy.mean())


def one_seed(seed, alpha, shift=1.0, recal_n=0):
    sim = SmartHomeSimulator(seed=1000)  # fixed world physics
    rng = np.random.default_rng(seed)
    tr = sim.sample_subjects(24, rng); al = sim.sample_subjects(10, rng)
    ca = sim.sample_subjects(14, rng); te = sim.sample_subjects(24, rng, shift=shift)
    Xtr, ytr, _ = sim.sample(tr, 150, rng); Xal, yal, _ = sim.sample(al, 150, rng)
    Xca, yca, _ = sim.sample(ca, 150, rng); Xte, yte, _ = sim.sample(te, 150, rng)
    cc = ConformalCascade(sim.tier_slices(), TIER_ENERGY, alpha=alpha, lam=LAM).fit(Xtr, ytr)
    Ecum = cc.energy_cum()
    res = {}
    # --- Ours (optimised budget), calibrated on disjoint split
    cc.allocate(Xal, yal)
    if recal_n:  # small on-site recalibration set from the deployment distribution
        rs = sim.sample_subjects(4, rng, shift=shift); Xr, yr, _ = sim.sample(rs, recal_n // 4, rng)
        cc.calibrate(np.vstack([Xca, Xr]) if False else Xr, yr)
    else:
        cc.calibrate(Xca, yca)
    s, a, e = cc.predict(Xte); res["AmI-CC (opt. budget)"] = metrics(yte, a, e)
    res["AmI-CC (opt. budget)"]["alphas"] = cc.alphas.tolist()
    # --- Ours ablation: equal budget split
    cc.set_equal_budget().calibrate(Xca, yca) if not recal_n else cc.set_equal_budget().calibrate(Xr, yr)
    s, a, e = cc.predict(Xte); res["AmI-CC (equal split)"] = metrics(yte, a, e)
    # --- Conformal, full sensing always (single tier 3)
    P = cc.probs(Xca); q3 = conformal_q(1 - P[2][np.arange(len(yca)), yca], alpha)
    Pt = cc.probs(Xte); inset = (1 - Pt[2]) <= q3; single = inset.sum(1) == 1
    a = np.where(single, inset.argmax(1), -1); res["Conformal, always full sensing"] = metrics(yte, a, np.full(len(yte), Ecum[2]))
    # --- Naive confidence-threshold cascade: one tau tuned on cal split so cal error among *all* <= alpha
    Pc = cc.probs(Xca)
    def run_tau(P, tau):
        n = len(P[0]); stop = np.full(n, 2); act = np.full(n, -1); done = np.zeros(n, bool)
        for t in range(3):
            ok = (P[t].max(1) >= tau) & ~done
            act[ok] = P[t].argmax(1)[ok]; stop[ok] = t; done |= ok
        act[~done] = P[2].argmax(1)[~done]  # naive: forced decision at last tier (no deferral)
        return stop, act
    best = 1.0
    for tau in np.linspace(0.3, 0.999, 120):
        st, ac = run_tau(Pc, tau)
        if (ac != yca).mean() <= alpha: best = tau; break
    st, ac = run_tau(Pt, best); res["Confidence-threshold cascade"] = metrics(yte, ac, Ecum[st])
    # --- Fixed-tier argmax baselines
    for t, name in [(0, "Tier-1 sensors only"), (2, "All sensors always (argmax)")]:
        res[name] = metrics(yte, Pt[t].argmax(1), np.full(len(yte), Ecum[t]))
    return res


def aggregate(runs):
    names = runs[0].keys(); out = {}
    for n in names:
        out[n] = {}
        for k in runs[0][n]:
            if k == "alphas": continue
            v = np.array([r[n][k] for r in runs]); out[n][k] = [float(v.mean()), float(v.std(ddof=1))]
        out[n]["viol_rate"] = None
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    R = {"main": {}, "shift": {}, "recal": {}, "alloc": {}}
    for al in ALPHAS:
        runs = [one_seed(s, al) for s in range(N_SEEDS)]
        agg = aggregate(runs)
        for n in agg:
            fa = np.array([r[n]["false_act"] for r in runs]); agg[n]["viol_rate"] = float((fa > al).mean())
        R["main"][str(al)] = agg
        R["alloc"][str(al)] = np.mean([r["AmI-CC (opt. budget)"]["alphas"] for r in runs], 0).tolist()
        print("alpha", al, {n: (round(agg[n]["false_act"][0], 4), round(agg[n]["energy"][0], 1), round(agg[n]["defer"][0], 3)) for n in agg}, flush=True)
    al = 0.05
    for sh in [1.0, 1.5, 2.0, 3.0]:
        runs = [one_seed(s, al, shift=sh) for s in range(N_SEEDS)]
        R["shift"][str(sh)] = aggregate(runs)
        runs_r = [one_seed(s, al, shift=sh, recal_n=800) for s in range(N_SEEDS)]
        R["recal"][str(sh)] = aggregate(runs_r)
        print("shift", sh, R["shift"][str(sh)]["AmI-CC (opt. budget)"]["false_act"], "recal", R["recal"][str(sh)]["AmI-CC (opt. budget)"]["false_act"], flush=True)
    json.dump(R, open(os.path.join(OUT, "results.json"), "w"), indent=1)
