import json, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = json.load(open(os.path.join(os.path.dirname(__file__), "..", "results", "results.json")))
OUT = os.path.join(os.path.dirname(__file__), "..", "results")
names = ["AmI-CC (opt. budget)", "AmI-CC (equal split)", "Conformal, always full sensing", "Confidence-threshold cascade", "All sensors always (argmax)"]
col = dict(zip(names, ["#1b6ca8", "#7fb3d5", "#d98a2b", "#b23a48", "#6b6b6b"]))
al = sorted(R["main"], key=float)
fig, ax = plt.subplots(1, 3, figsize=(13, 3.6))
for n in names:
    ax[0].plot([float(a) for a in al], [R["main"][a][n]["false_act"][0] for a in al], "o-", c=col[n], label=n)
    ax[1].plot([float(a) for a in al], [R["main"][a][n]["energy"][0] for a in al], "o-", c=col[n])
    ax[2].plot([float(a) for a in al], [R["main"][a][n]["defer"][0] for a in al], "o-", c=col[n])
ax[0].plot([0, .1], [0, .1], "k--", lw=.8, label="target bound y=α")
for a_, t in zip(ax, ["False-actuation rate", "Energy / decision (norm. units)", "Deferral rate"]):
    a_.set_title(t); a_.set_xlabel("risk budget α")
ax[0].legend(fontsize=6); plt.tight_layout(); plt.savefig(os.path.join(OUT, "fig_main.png"), dpi=160)
fig, ax = plt.subplots(figsize=(5, 3.4)); sh = sorted(R["shift"], key=float)
ax.plot([float(s) for s in sh], [R["shift"][s]["AmI-CC (opt. budget)"]["false_act"][0] for s in sh], "o-", label="calibrated pre-deployment")
ax.plot([float(s) for s in sh], [R["recal"][s]["AmI-CC (opt. budget)"]["false_act"][0] for s in sh], "s-", label="+ on-site recalibration")
ax.axhline(.05, c="k", ls="--", lw=.8); ax.set_xlabel("subject-shift severity"); ax.set_ylabel("false-actuation rate"); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "fig_shift.png"), dpi=160)
