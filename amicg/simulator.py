"""Synthetic multi-tier smart-home benchmark.

Each *subject* (household/occupant) produces samples of one of K ambient intents.
Sensing is organised in tiers of increasing energy cost and discriminative power:
  tier 1: passive low-power (PIR, door, light, time-of-day)        -> cheap, ambiguous
  tier 2: + plug-power / audio-level / BLE-RSSI                     -> medium
  tier 3: + camera / mmWave embedding                               -> expensive, sharp
Feature vectors are cumulative (tier t sees blocks 1..t). Each subject has its own
offset/scale per block (habits, sensor placement) => inter-subject covariate shift.
"""
import numpy as np

TIER_ENERGY = np.array([1.0, 6.0, 40.0])  # normalised energy units per sensing event (incl. wake-up)
INTENTS = ["idle", "enter_home", "cooking", "watch_tv", "sleep", "leave_home", "exercise", "fall_risk"]


class SmartHomeSimulator:
    def __init__(self, n_classes=8, dims=(6, 8, 12), sep=(3.0, 3.6, 5.5), subject_sd=0.5, seed=0):
        self.K, self.dims, self.sep, self.subject_sd = n_classes, dims, sep, subject_sd
        rng = np.random.default_rng(seed)
        # class means per block; tier-1 means are drawn in clusters so some intents are confusable
        self.mu = []
        for d, s in zip(dims, sep):
            m = rng.normal(size=(n_classes, d))
            m /= np.linalg.norm(m, axis=1, keepdims=True)
            self.mu.append(m * s)
        # make tier-1 intent pairs (0,1),(2,3),(4,5),(6,7) strongly confusable at low tiers
        for b in (0, 1):
            for a in (2, 4, 6):
                self.mu[b][a + 1] = self.mu[b][a] + 0.22 * self.mu[b][a + 1] / max(1e-9, np.linalg.norm(self.mu[b][a + 1])) * self.sep[b] * (1.0 if b == 0 else 1.3)
        self.prior = np.array([.22, .10, .12, .16, .14, .08, .10, .08])[:n_classes]
        self.prior /= self.prior.sum()

    def sample_subjects(self, n_sub, rng, shift=1.0):
        return [[rng.normal(scale=self.subject_sd * shift, size=d) for d in self.dims] for _ in range(n_sub)]

    def sample(self, subjects, n_per, rng, noise=1.0):
        X, y, sid = [], [], []
        for i, sub in enumerate(subjects):
            yy = rng.choice(self.K, size=n_per, p=self.prior)
            blocks = [self.mu[b][yy] + sub[b] + rng.normal(scale=noise, size=(n_per, self.dims[b])) for b in range(3)]
            X.append(np.hstack(blocks)); y.append(yy); sid.append(np.full(n_per, i))
        return np.vstack(X), np.concatenate(y), np.concatenate(sid)

    def tier_slices(self):
        ends = np.cumsum(self.dims)
        return [slice(0, e) for e in ends]
