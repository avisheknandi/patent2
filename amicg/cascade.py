"""Conformal sensing cascade with energy-optimal risk-budget allocation.

Decision rule at tier t (only tiers 1..t have been powered):
  C_t(x) = {k : 1 - p_t,k(x) <= q_t}                (split-conformal LAC set, miscoverage alpha_t)
  |C_t| == 1 -> ACTUATE the single intent, stop (higher tiers never woken)
  else        -> wake tier t+1; at last tier |C|!=1 -> DEFER (ask user / no autonomous action)
Wrong actuation requires y not in C_t for the tier that stopped, so
  P(wrong actuation) <= sum_t alpha_t  (union bound) -- the *risk budget* alpha.
Budget split (alpha_1..alpha_T) is chosen on a dedicated split to minimise
  J = E[energy] + lambda * P(defer)  s.t.  sum alpha_t <= alpha ,
then thresholds q_t are calibrated on a disjoint split (keeps validity).
"""
import itertools
import numpy as np
from sklearn.linear_model import LogisticRegression


def conformal_q(scores, alpha):
    n = len(scores)
    k = int(np.ceil((n + 1) * (1 - alpha)))
    if k > n:
        return np.inf
    return np.sort(scores)[k - 1]


class ConformalCascade:
    def __init__(self, slices, energy, alpha=0.05, lam=20.0, grid=20, C=1.0):
        self.slices, self.energy, self.alpha, self.lam, self.grid, self.C = slices, np.asarray(energy), alpha, lam, grid, C
        self.T = len(slices)

    def fit(self, X, y):
        self.clfs = [LogisticRegression(C=self.C, max_iter=500).fit(X[:, s], y) for s in self.slices]
        return self

    def probs(self, X):
        return [c.predict_proba(X[:, s]) for c, s in zip(self.clfs, self.slices)]

    def _scores(self, P, y):
        return [1 - p[np.arange(len(y)), y] for p in P]

    @staticmethod
    def _run(P, qs):
        """Vectorised cascade. Returns stop tier (0-based, T-1 if deferred at end), action (-1 = defer)."""
        n, T = len(P[0]), len(P)
        stop = np.full(n, T - 1); act = np.full(n, -1); done = np.zeros(n, bool)
        for t in range(T):
            inset = (1 - P[t]) <= qs[t]
            single = inset.sum(1) == 1
            new = single & ~done
            act[new] = inset[new].argmax(1); stop[new] = t; done |= new
        return stop, act

    def allocate(self, X, y):
        P = self.probs(X); S = self._scores(P, y)
        best, step = None, self.alpha / self.grid
        for a in itertools.product(range(self.grid + 1), repeat=self.T - 1):
            if sum(a) > self.grid: continue
            al = np.array(list(a) + [self.grid - sum(a)]) * step
            if al[-1] <= 0 and False: continue
            qs = [conformal_q(S[t], max(al[t], 1e-9)) if al[t] > 0 else np.inf for t in range(self.T)]
            stop, act = self._run(P, qs)
            J = self.energy_cum()[stop].mean() + self.lam * (act < 0).mean()
            if best is None or J < best[0]: best = (J, al)
        self.alphas = best[1]; return self

    def energy_cum(self):
        return np.cumsum(self.energy)

    def calibrate(self, X, y):
        S = self._scores(self.probs(X), y)
        self.qs = [conformal_q(S[t], self.alphas[t]) if self.alphas[t] > 0 else np.inf for t in range(self.T)]
        return self

    def set_equal_budget(self):
        self.alphas = np.full(self.T, self.alpha / self.T); return self

    def predict(self, X):
        P = self.probs(X)
        stop, act = self._run(P, self.qs)
        return stop, act, self.energy_cum()[stop]
