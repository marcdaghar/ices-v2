# src/analysis/minimum_core.py
"""
Minimum Publishable Core (MPC) for ICES v2.
"""

from typing import Dict, List

class MinimumPublishableCore:
    """
    Defines the minimum publishable core for ICES v2.
    """
    
    def __init__(self):
        self.core = self._define_core()
        self.checklist = self._define_checklist()

    def _define_core(self) -> Dict[str, List[str]]:
        """Define core components for Paper 1."""
        return {
            "required": [
                "4-layer architecture (Agents, Economics, Institutions, Metrics)",
                "Household, Merchant, Farmer agents",
                "Bimetallic and Fiat monetary systems",
                "Commodity Reserve Department (CRD)",
                "Zakat, Waqf, Hisba institutions",
                "Civilization Index (CI)",
                "Hierarchical Bayesian Calibration",
                "Global Sensitivity Analysis (Sobol)",
                "Out-of-Sample Prediction Protocol",
                "Baseline Comparisons (Linear, VAR, Ecology-Only)",
                "Falsifiability Criteria (A, B, C, D)"
            ],
            "excluded": [
                "Neurocognitive agents",
                "Reinforcement learning for moral formation",
                "Dynamic networks",
                "Advanced attractor analysis (TDA, RQA)",
                "Basin transitions",
                "Energy EROI tracking"
            ]
        }

    def _define_checklist(self) -> Dict[str, List[str]]:
        """Define publication checklist."""
        return {
            "model": ["4-layer architecture", "Zakat, Waqf, Hisba, CRD implemented"],
            "calibration": ["Hierarchical Bayesian calibration", "Partial pooling by family"],
            "validation": ["Out-of-sample prediction", "Baseline comparisons"],
            "analysis": ["Global sensitivity analysis (Sobol)", "Falsifiability criteria tested"]
        }

    def get_core(self) -> Dict[str, List[str]]:
        return self.core

    def get_checklist(self) -> Dict[str, List[str]]:
        return self.checklist
