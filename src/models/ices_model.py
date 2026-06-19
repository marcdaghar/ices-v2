# src/models/ices_model.py
"""
ICES v2 - Islamic Civilizational Economic Simulator
Full 4-layer architecture with complete modules.

This is the main model file that imports and orchestrates:
- Agents from src/agents/
- Layers from src/layers/
- Analysis from src/analysis/
"""

import numpy as np
import pandas as pd
import random
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

# Import agents
from src.agents import (
    BaseAgent, MoralState,
    Household, Merchant, Farmer,
    WaqfInstitution, Scholar, Emirate
)

# Import layers
from src.layers import (
    AgentPhysics, EconomicMechanisms, InstitutionalLayer, MetricsLayer
)

# Import analysis modules
from src.analysis import (
    SobolAnalyzer,
    HierarchicalBayesianCalibrator,
    FalsifiabilityTester,
    PredictionProtocol,
    BaselineComparer,
    MinimumPublishableCore
)

# Mesa imports
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector


# ============================================================
# MAIN ICES MODEL
# ============================================================

class ICESModel(Model):
    """
    Full ICES v2 model with 4-layer architecture.
    
    This model integrates:
    - Layer 1: Agent Physics (src/layers/agent_physics.py)
    - Layer 2: Economic Mechanisms (src/layers/economic_mechanisms.py)
    - Layer 3: Institutions (src/layers/institutions.py)
    - Layer 4: Metrics (src/layers/metrics.py)
    
    Agents:
    - Household (src/agents/household.py)
    - Merchant (src/agents/merchant.py)
    - Farmer (src/agents/farmer.py)
    - Waqf Institution (src/agents/waqf.py)
    - Scholar (src/agents/scholar.py)
    - Emirate (src/agents/emir.py)
    """
    
    def __init__(
        self,
        width: int = 20,
        height: int = 20,
        n_households: int = 60,
        n_merchants: int = 20,
        n_farmers: int = 20,
        use_zakat: bool = True,
        use_waqf: bool = True,
        use_hisba: bool = True,
        use_crd: bool = True,
        monetary_system: str = "dinar",
        seed: Optional[int] = None,
        verbose: bool = False
    ):
        """
        Initialize the ICES model with specified parameters.
        
        Args:
            width: Grid width
            height: Grid height
            n_households: Number of household agents
            n_merchants: Number of merchant agents
            n_farmers: Number of farmer agents
            use_zakat: Enable Zakat institution
            use_waqf: Enable Waqf institution
            use_hisba: Enable Hisba market supervision
            use_crd: Enable Commodity Reserve Department
            monetary_system: "dinar", "fiat", or "bitcoin"
            seed: Random seed for reproducibility
            verbose: Print progress information
        """
        super().__init__(seed=seed)
        
        # Configuration
        self.config = {
            "width": width,
            "height": height,
            "n_households": n_households,
            "n_merchants": n_merchants,
            "n_farmers": n_farmers,
            "use_zakat": use_zakat,
            "use_waqf": use_waqf,
            "use_hisba": use_hisba,
            "use_crd": use_crd,
            "monetary_system": monetary_system,
            "seed": seed,
            "verbose": verbose
        }
        
        self.verbose = verbose
        self.year = 0
        self.total_agents = n_households + n_merchants + n_farmers
        
        # ===== LAYER 1: AGENT PHYSICS =====
        self.agent_physics = AgentPhysics(width, height)
        if self.verbose:
            print(f"[ICES] Layer 1 initialized: AgentPhysics (grid {width}x{height})")
        
        # ===== LAYER 2: ECONOMIC MECHANISMS =====
        self.economic = EconomicMechanisms(
            monetary_system=monetary_system,
            use_crd=use_crd
        )
        if self.verbose:
            print(f"[ICES] Layer 2 initialized: EconomicMechanisms ({monetary_system})")
        
        # ===== LAYER 3: INSTITUTIONS =====
        self.institutions = InstitutionalLayer(
            use_zakat=use_zakat,
            use_waqf=use_waqf,
            use_hisba=use_hisba
        )
        self.institutions.initialize()
        self.emirate = self.institutions.emirate
        self.waqf = self.institutions.waqf
        if self.verbose:
            print(f"[ICES] Layer 3 initialized: InstitutionalLayer (zakat={use_zakat}, waqf={use_waqf})")
        
        # ===== LAYER 4: METRICS =====
        self.metrics_layer = MetricsLayer()
        if self.verbose:
            print(f"[ICES] Layer 4 initialized: MetricsLayer")
        
        # ===== SPACE AND SCHEDULE =====
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        
        # ===== CREATE AGENTS =====
        self.agents = []
        self._create_agents(n_households, n_merchants, n_farmers)
        
        # ===== DATA COLLECTOR =====
        self.datacollector = DataCollector(
            model_reporters={
                "Civilization_Index": self.compute_civilization_index,
                "Avg_Wealth": self.compute_avg_wealth,
                "Avg_Trust": self.compute_avg_trust,
                "Gini": self.compute_gini,
                "Zakat_Treasury": lambda: self.emirate.zakat_treasury if self.emirate else 0,
                "Waqf_Endowment": lambda: self.waqf.endowment if self.waqf else 0,
                "Money_Supply": lambda: self.economic.money_supply if self.economic else 0,
                "Price_Level": lambda: self.economic.price_level if self.economic else 100,
                "Justice_Index": lambda: self.emirate.justice_index if self.emirate else 50,
                "Ecological_Debt": lambda: self.agent_physics.ecological_debt if self.agent_physics else 0,
                "EROI": lambda: self.agent_physics.get_energy_return_on_investment() if self.agent_physics else 1.0
            },
            agent_reporters={
                "Wealth": lambda a: a.wealth if hasattr(a, 'wealth') else 0,
                "Trust": lambda a: a.trust if hasattr(a, 'trust') else 0,
                "Taqwa": lambda a: a.moral_state.taqwa if hasattr(a, 'moral_state') else 0,
                "Gold": lambda a: a.gold if hasattr(a, 'gold') else 0,
                "Silver": lambda a: a.silver if hasattr(a, 'silver') else 0
            }
        )
        
        if self.verbose:
            print(f"[ICES] Model initialized with {self.total_agents} agents")
            print(f"[ICES] Config: {self.config}")

    def _create_agents(self, n_households: int, n_merchants: int, n_farmers: int):
        """Create all agents and add them to the model."""
        # Households
        for i in range(n_households):
            wealth = random.uniform(10, 100)
            h = Household(i, self, initial_wealth=wealth)
            self.grid.place_agent(h, h.location)
            self.schedule.add(h)
            self.agents.append(h)
        
        # Merchants
        for i in range(n_merchants):
            wealth = random.uniform(50, 500)
            m = Merchant(n_households + i, self, initial_wealth=wealth)
            self.grid.place_agent(m, m.location)
            self.schedule.add(m)
            self.agents.append(m)
        
        # Farmers
        for i in range(n_farmers):
            wealth = random.uniform(10, 50)
            land_quality = random.uniform(0.3, 0.9)
            f = Farmer(n_households + n_merchants + i, self, initial_wealth=wealth, land_quality=land_quality)
            self.grid.place_agent(f, f.location)
            self.schedule.add(f)
            self.agents.append(f)

    # ============================================================
    # STEP METHODS
    # ============================================================

    def step(self):
        """Advance the model by one time step."""
        self.year += 1
        
        # ===== LAYER 1: AGENT PHYSICS =====
        # Update ecology based on agent activities
        self.agent_physics.update_ecology(self.agents)
        
        # ===== AGENTS =====
        self.schedule.step()
        
        # ===== LAYER 2: ECONOMIC MECHANISMS =====
        self.economic.step(self.agents)
        
        # ===== LAYER 3: INSTITUTIONS =====
        self.institutions.step(self.agents, self.year)
        
        # Pass market and emirate references to agents
        for agent in self.agents:
            if hasattr(agent, 'pay_zakat'):
                agent.pay_zakat(self.economic.market, self.emirate)
        
        # ===== LAYER 4: METRICS =====
        self.metrics_layer.compute_civilization_index(self.agents, self.emirate)
        
        # ===== DATA COLLECTION =====
        self.datacollector.collect(self)
        
        # ===== ECOLOGICAL MONITORING =====
        if self.year % 12 == 0 and self.verbose:
            eco = self.agent_physics.to_dict()
            print(f"[Year {self.year}] Ecology: water={eco['water_availability']:.1f}, EROI={eco['eroi']:.2f}")

    def run(self, n_steps: int = 100, progress_bar: bool = True) -> pd.DataFrame:
        """
        Run the simulation for a specified number of steps.
        
        Args:
            n_steps: Number of steps to run
            progress_bar: Show progress bar (requires tqdm)
        
        Returns:
            DataFrame with collected data
        """
        if progress_bar:
            try:
                from tqdm import tqdm
                for _ in tqdm(range(n_steps), desc="Running simulation"):
                    self.step()
            except ImportError:
                for _ in range(n_steps):
                    self.step()
        else:
            for _ in range(n_steps):
                self.step()
        
        return self.datacollector.get_model_vars_dataframe()

    # ============================================================
    # COMPUTATION METHODS
    # ============================================================

    def compute_civilization_index(self) -> float:
        """Compute Civilization Index (CI)."""
        return self.metrics_layer.compute_civilization_index(self.agents, self.emirate)

    def compute_avg_wealth(self) -> float:
        """Compute average wealth across all agents."""
        return np.mean([a.wealth for a in self.agents])

    def compute_avg_trust(self) -> float:
        """Compute average trust across all agents."""
        trusts = [a.trust for a in self.agents if hasattr(a, 'trust')]
        return np.mean(trusts) if trusts else 0.0

    def compute_gini(self) -> float:
        """Compute Gini coefficient."""
        return self.metrics_layer.compute_gini(self.agents)

    def get_agent_data(self) -> pd.DataFrame:
        """Get agent-level data as DataFrame."""
        return pd.DataFrame([a.to_dict() for a in self.agents])

    def get_layer_data(self) -> Dict[str, Any]:
        """Get layer-level data."""
        return {
            "agent_physics": self.agent_physics.to_dict(),
            "economic": {
                "monetary_system": self.economic.monetary_system,
                "price_level": self.economic.price_level,
                "money_supply": self.economic.money_supply,
                "transaction_volume": self.economic.transaction_volume
            },
            "institutions": self.institutions.to_dict(),
            "metrics": self.metrics_layer.to_dict()
        }

    # ============================================================
    # ANALYSIS METHODS
    # ============================================================

    def run_sensitivity_analysis(self, params: Dict[str, Tuple[float, float]], n_samples: int = 1000) -> Dict:
        """
        Run global sensitivity analysis using Sobol indices.
        
        Args:
            params: Dict mapping parameter name to (min, max) bounds
            n_samples: Number of samples for Saltelli's method
        
        Returns:
            Sobol analysis results
        """
        def model_func(p: Dict[str, float]) -> Dict[str, float]:
            # Run simulation with given parameters
            for key, value in p.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self.run(50)
            return {"CI": self.compute_civilization_index()}
        
        analyzer = SobolAnalyzer(model_func, params)
        results = analyzer.analyze(n_samples=n_samples)
        return results

    def run_calibration(self, data: Dict[str, pd.DataFrame], families: Dict[str, List[str]]) -> Any:
        """
        Run hierarchical Bayesian calibration.
        
        Args:
            data: Dict mapping civilization to DataFrame
            families: Dict mapping family name to list of civilizations
        
        Returns:
            PyMC trace object
        """
        calibrator = HierarchicalBayesianCalibrator(data, families)
        return calibrator.calibrate()

    def run_prediction(self, data: Dict[str, pd.DataFrame], civilization: str, n_sims: int = 100) -> Dict:
        """
        Run out-of-sample prediction protocol.
        
        Args:
            data: Historical data for all civilizations
            civilization: Name of civilization to predict
            n_sims: Number of simulations for uncertainty
        
        Returns:
            Prediction results
        """
        protocol = PredictionProtocol(self, data)
        return protocol.run(civilization, n_sims=n_sims)

    def run_falsifiability_tests(self, params: Dict[str, float]) -> Dict:
        """
        Run falsifiability tests.
        
        Args:
            params: Model parameters
        
        Returns:
            Falsifiability test results
        """
        def ices_func(p: Dict[str, float]) -> Dict[str, float]:
            # Run ICES with given parameters
            for key, value in p.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self.run(50)
            return {"CI": self.compute_civilization_index()}
        
        def eco_func() -> Dict[str, float]:
            # Run ecology-only model
            eco_model = ICESModel(
                use_zakat=False,
                use_waqf=False,
                use_hisba=False,
                use_crd=False,
                n_households=20,
                n_merchants=10,
                n_farmers=10
            )
            eco_model.run(50)
            return {"CI": eco_model.compute_civilization_index()}
        
        tester = FalsifiabilityTester(ices_func, eco_func)
        return tester.test_all_criteria(params)

    def compare_to_baselines(self, data: Dict[str, pd.DataFrame], civilization: str) -> Dict:
        """
        Compare ICES against baseline models.
        
        Args:
            data: Historical data
            civilization: Name of civilization
        
        Returns:
            Comparison results
        """
        comparer = BaselineComparer(self, data)
        return comparer.compare(civilization, {})

    # ============================================================
    # SAVE AND LOAD
    # ============================================================

    def save_results(self, path: str = "results/paper1"):
        """Save simulation results to disk."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save model data
        df = self.datacollector.get_model_vars_dataframe()
        df.to_csv(path / "simulation_results.csv", index=False)
        
        # Save agent data
        agent_df = self.get_agent_data()
        agent_df.to_csv(path / "agent_data.csv", index=False)
        
        # Save layer data
        import json
        with open(path / "layer_data.json", "w") as f:
            json.dump(self.get_layer_data(), f, indent=2, default=str)
        
        # Save configuration
        with open(path / "config.json", "w") as f:
            json.dump(self.config, f, indent=2)
        
        return path

    @classmethod
    def from_config(cls, config_path: str) -> "ICESModel":
        """Create model from configuration file."""
        import json
        with open(config_path, "r") as f:
            config = json.load(f)
        return cls(**config)


# ============================================================
# EXPERIMENT RUNNER
# ============================================================

class ICESExperimentRunner:
    """
    Runner for conducting controlled experiments with ICES.
    """
    
    def __init__(self, base_config: Dict):
        self.base_config = base_config

    def run_experiment(
        self,
        config_name: str,
        config_overrides: Dict,
        n_steps: int = 100,
        n_replicates: int = 5
    ) -> pd.DataFrame:
        """
        Run a single experiment configuration with multiple replicates.
        """
        all_results = []
        
        for replicate in range(n_replicates):
            config = self.base_config.copy()
            config.update(config_overrides)
            config['seed'] = int(np.random.randint(0, 1000000) + replicate)
            config['verbose'] = False
            
            model = ICESModel(**config)
            df = model.run(n_steps, progress_bar=False)
            df['replicate'] = replicate
            df['config'] = config_name
            all_results.append(df)
        
        return pd.concat(all_results, ignore_index=True)

    def run_batch(
        self,
        configs: Dict[str, Dict],
        n_steps: int = 100,
        n_replicates: int = 5
    ) -> Dict[str, pd.DataFrame]:
        """
        Run a batch of experiments with different configurations.
        """
        results = {}
        for config_name, config_overrides in configs.items():
            print(f"Running: {config_name}")
            df = self.run_experiment(config_name, config_overrides, n_steps, n_replicates)
            results[config_name] = df
        return results


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    print("="*60)
    print("ICES v2 - Islamic Civilizational Economic Simulator")
    print("="*60)
    
    # Create model
    model = ICESModel(
        n_households=60,
        n_merchants=20,
        n_farmers=20,
        use_zakat=True,
        use_waqf=True,
        use_crd=True,
        monetary_system="dinar",
        verbose=True
    )
    
    # Run simulation
    print("\nRunning simulation...")
    df = model.run(100, progress_bar=True)
    
    # Print results
    print("\n" + "="*60)
    print("SIMULATION RESULTS")
    print("="*60)
    print(f"Final Civilization Index: {df['Civilization_Index'].iloc[-1]:.3f}")
    print(f"Final Gini Coefficient: {df['Gini'].iloc[-1]:.3f}")
    print(f"Final Average Trust: {df['Avg_Trust'].iloc[-1]:.1f}")
    print(f"Final Average Wealth: {df['Avg_Wealth'].iloc[-1]:.1f}")
    
    # Save results
    results_dir = model.save_results()
    print(f"\nResults saved to: {results_dir}")
    
    print("\n✅ ICES v2 setup complete!")
