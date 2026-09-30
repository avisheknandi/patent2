import sys, os, unittest
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from amicg import SmartHomeSimulator, ConformalCascade, TIER_ENERGY
from amicg.cascade import conformal_q


class T(unittest.TestCase):
    def test_quantile_coverage(self):
        rng = np.random.default_rng(0); cov = []
        for _ in range(300):
            s = rng.random(200); q = conformal_q(s, 0.1); cov.append((rng.random(400) <= q).mean())
        self.assertGreaterEqual(np.mean(cov), 0.895)

    def test_budget_and_energy(self):
        sim = SmartHomeSimulator(seed=1000); rng = np.random.default_rng(1)
        d = lambda n, k: sim.sample(sim.sample_subjects(n, rng), k, rng)
        Xtr, ytr, _ = d(20, 120); Xa, ya, _ = d(8, 120); Xc, yc, _ = d(12, 120); Xt, yt, _ = d(20, 120)
        cc = ConformalCascade(sim.tier_slices(), TIER_ENERGY, alpha=0.05).fit(Xtr, ytr).allocate(Xa, ya).calibrate(Xc, yc)
        self.assertLessEqual(cc.alphas.sum(), 0.05 + 1e-9)
        stop, act, e = cc.predict(Xt)
        self.assertLessEqual(((act >= 0) & (act != yt)).mean(), 0.05 + 0.015)
        self.assertLess(e.mean(), TIER_ENERGY.sum())


if __name__ == "__main__":
    unittest.main()
