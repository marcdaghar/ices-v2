# src/layers/metrics.py
"""
Layer 4: Metrics - Civilization outcomes.
"""

import numpy as np
from typing import List, Dict

class MetricsLayer:
    """Layer 4: Metrics - Civilization outcomes."""
    
    def __init__(self):
        self.weights = {
            "wealth": 0.25,
            "trust": 0.25,
            "justice": 0.20,
            "ecology": 0.15,
            "spiritual": 0.15
        }
        self.history = []

    def compute_civilization_index(self, agents: List, emirate) -> float:
        """Compute Civilization Index (CI)."""
        metrics = self.compute_all_metrics(agents, emirate)
        ci = sum(metrics[k] * self.weights[k] for k in self.weights)
        self.history.append({"ci": ci, "metrics": metrics})
        return ci

    def compute_all_metrics(self, agents: List, emirate) -> Dict[str, float]:
        """Compute all civilization metrics."""
        # Wealth Index (W)
        wealths = [a.wealth for a in agents]
        mean_wealth = np.mean(wealths) if wealths else 0
        wealth_index = mean_wealth / 100
        
        # Trust Index (T)
        trusts = [a.trust for a in agents if hasattr(a, 'trust')]
        trust_index = np.mean(trusts) / 100 if trusts else 0.5
        
        # Justice Index (J)
        gini = self.compute_gini(agents)
        market_access = self.compute_market_access(agents)
        hisba_effect = 1 - emirate.corruption_level if emirate else 0.9
        justice_index = (1 - gini) * 0.5 + market_access * 0.3 + hisba_effect * 0.2
        
        # Ecological Index (E)
        ecology = 0.8  # Placeholder
        
        # Spiritual Capital (S)
        zakat_ratio = sum(a.zakat_paid for a in agents) / max(1, sum(a.wealth for a in agents))
        waqf_participation = sum(1 for a in agents if a.waqf_contributions > 0) / max(1, len(agents))
        honesty = np.mean([a.moral_state.trustworthiness for a in agents if hasattr(a, 'moral_state')])
        spiritual_index = zakat_ratio * 0.3 + waqf_participation * 0.4 + honesty * 0.3
        
        return {
            "wealth": wealth_index,
            "trust": trust_index,
            "justice": justice_index,
            "ecology": ecology,
            "spiritual": spiritual_index
        }

    @staticmethod
    def compute_gini(agents: List) -> float:
        """Compute Gini coefficient of wealth distribution."""
        wealths = sorted([a.wealth for a in agents])
        n = len(wealths)
        if n == 0 or sum(wealths) == 0:
            return 0.5
        numerator = 2 * sum((i+1) * wealths[i] for i in range(n))
        denominator = n * sum(wealths)
        return max(0, min(1, 1 - numerator / denominator))

    @staticmethod
    def compute_market_access(agents: List) -> float:
        """Compute market access index."""
        trusts = [a.trust for a in agents if hasattr(a, 'trust')]
        if trusts:
            return np.mean(trusts) / 100
        return 0.5

    def to_dict(self) -> Dict:
        return {
            "weights": self.weights,
            "history": self.history[-10:] if self.history else []
        }
