# src/analysis/hierarchical_bayes.py
"""
Hierarchical Bayesian Calibration with Partial Pooling.
"""

import pymc as pm
import numpy as np
import pandas as pd
import arviz as az
from typing import Dict, List, Optional, Tuple

class HierarchicalBayesianCalibrator:
    """
    Hierarchical Bayesian calibration with partial pooling by civilization family.
    """
    
    def __init__(
        self,
        data: Dict[str, pd.DataFrame],
        families: Dict[str, List[str]],
        observed_vars: List[str] = ["population"]
    ):
        self.data = data
        self.families = families
        self.observed_vars = observed_vars
        self.family_names = list(families.keys())
        self.civ_names = list(data.keys())

    def build_model(self, n_years: int) -> pm.Model:
        """Build hierarchical Bayesian model."""
        with pm.Model() as model:
            # Hyperpriors
            mu_trust = pm.Normal("mu_trust", mu=0.5, sigma=0.2)
            sigma_trust = pm.HalfNormal("sigma_trust", sigma=0.1)
            mu_institutional = pm.Normal("mu_institutional", mu=0.5, sigma=0.2)
            sigma_institutional = pm.HalfNormal("sigma_institutional", sigma=0.1)
            
            # Family-level parameters
            family_trust = pm.Normal(
                "family_trust",
                mu=mu_trust,
                sigma=sigma_trust,
                shape=len(self.family_names)
            )
            family_institutional = pm.Normal(
                "family_institutional",
                mu=mu_institutional,
                sigma=sigma_institutional,
                shape=len(self.family_names)
            )
            
            # Civilization-level parameters
            for civ in self.civ_names:
                family_idx = self._get_family_index(civ)
                n_years_civ = len(self.data[civ])
                
                trust = pm.Normal(
                    f"trust_{civ}",
                    mu=family_trust[family_idx],
                    sigma=0.05,
                    shape=n_years_civ
                )
                institutional = pm.Normal(
                    f"institutional_{civ}",
                    mu=family_institutional[family_idx],
                    sigma=0.05,
                    shape=n_years_civ
                )
                
                for var in self.observed_vars:
                    if var in self.data[civ].columns:
                        pm.Normal(
                            f"{var}_obs_{civ}",
                            mu=0.4 * trust + 0.3 * institutional,
                            sigma=0.05,
                            observed=self.data[civ][var].values / 100
                        )
        return model

    def _get_family_index(self, civ: str) -> int:
        for idx, (family, members) in enumerate(self.families.items()):
            if civ in members:
                return idx
        return 0

    def calibrate(self, n_samples: int = 2000, tune: int = 1000, chains: int = 4) -> az.InferenceData:
        """Run calibration."""
        n_years = max(len(df) for df in self.data.values())
        model = self.build_model(n_years)
        with model:
            trace = pm.sample(n_samples, tune=tune, chains=chains, return_inferencedata=True)
        return trace
