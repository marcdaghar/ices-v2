# src/analysis/sensitivity.py
"""
Global Sensitivity Analysis using Sobol indices.
Identifies which parameters drive model outcomes.
"""

import numpy as np
from SALib.sample import saltelli
from SALib.analyze import sobol
from typing import Dict, List, Tuple, Callable, Any

class SobolAnalyzer:
    """
    Computes first-order and total Sobol indices to identify driving parameters.
    """
    
    def __init__(
        self,
        model_func: Callable[[Dict[str, float]], Dict[str, Any]],
        params: Dict[str, Tuple[float, float]],
        output_key: str = "CI"
    ):
        self.model_func = model_func
        self.params = params
        self.output_key = output_key
        self.problem = {
            "num_vars": len(params),
            "names": list(params.keys()),
            "bounds": list(params.values())
        }

    def analyze(self, n_samples: int = 1000, print_to_console: bool = False) -> Dict[str, Any]:
        """Run Sobol analysis."""
        N = self.problem["num_vars"]
        if n_samples % (2 * N + 2) != 0:
            n_samples = n_samples + ((2 * N + 2) - (n_samples % (2 * N + 2)))
        
        param_values = saltelli.sample(self.problem, n_samples, calc_second_order=False)
        
        outputs = np.zeros([n_samples])
        for i, X in enumerate(param_values):
            param_dict = {name: X[j] for j, name in enumerate(self.problem["names"])}
            result = self.model_func(param_dict)
            outputs[i] = result[self.output_key]
        
        Si = sobol.analyze(self.problem, outputs, calc_second_order=False, print_to_console=print_to_console)
        
        driving_params = []
        for name, st in zip(self.problem["names"], Si["ST"]):
            if st > 0.05:
                driving_params.append({
                    "name": name,
                    "S1": Si["S1"][self.problem["names"].index(name)],
                    "ST": st
                })
        
        variance_explained = sum(p["ST"] for p in driving_params)
        
        return {
            "first_order": dict(zip(self.problem["names"], Si["S1"])),
            "total_order": dict(zip(self.problem["names"], Si["ST"])),
            "driving_params": driving_params,
            "n_driving": len(driving_params),
            "variance_explained": variance_explained,
            "n_samples": n_samples
        }

    def report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable report."""
        report = [
            "=== SOBOL SENSITIVITY ANALYSIS ===",
            f"Driving parameters: {results['n_driving']} (explaining {results['variance_explained']:.1%} of variance)",
            "\n--- Driving Parameters (ST > 0.05) ---"
        ]
        for p in results["driving_params"]:
            report.append(f"  {p['name']}: S1={p['S1']:.3f}, ST={p['ST']:.3f}")
        return "\n".join(report)
