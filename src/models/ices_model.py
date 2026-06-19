# src/models/ices_model.py
"""
ICES v2 - Islamic Civilizational Economic Simulator
Full 4-layer architecture with hierarchical Bayesian calibration.
"""

import numpy as np
import networkx as nx
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random
from typing import Dict, List, Tuple, Optional

# ============================================================
# LAYER 1: AGENT PHYSICS
# ============================================================

class MoralState:
    """Endogenous moral formation through reinforcement learning."""
    
    def __init__(self):
        self.taqwa = 0.5
        self.greed = 0.5
        self.solidarity = 0.5
        self.trustworthiness = 0.5

    def update_from_action(self, action: str, outcome: float):
        """Morality emerges from experience, not direct assignment."""
        if action == "honest_trade":
            self.taqwa += 0.01 * outcome
            self.trustworthiness += 0.01 * outcome
            self.greed -= 0.005 * (1 - outcome)
        elif action == "fraud":
            self.greed += 0.02 * outcome
            self.trustworthiness -= 0.03 * (1 + outcome)
            self.taqwa -= 0.02 * (1 + outcome)
        elif action == "zakat_payment":
            self.solidarity += 0.03 * outcome
            self.taqwa += 0.02 * outcome
        elif action == "hoarding":
            self.greed += 0.03 * outcome
            self.trustworthiness -= 0.02 * (1 + outcome)
        elif action == "waqf_contribution":
            self.solidarity += 0.04 * outcome
            self.trustworthiness += 0.01 * outcome
        
        # Keep within bounds
        self.taqwa = np.clip(self.taqwa, 0.0, 1.0)
        self.greed = np.clip(self.greed, 0.0, 1.0)
        self.solidarity = np.clip(self.solidarity, 0.0, 1.0)
        self.trustworthiness = np.clip(self.trustworthiness, 0.0, 1.0)


class BaseAgent(Agent):
    """Base agent class with trust, wealth, and moral state."""
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = random.uniform(10, 100)
        self.gold = self.wealth * 0.4
        self.silver = self.wealth * 0.3
        self.trust = random.uniform(20, 80)
        self.moral_state = MoralState()
        self.history = []
        self.zakat_paid = 0.0
        self.waqf_contributions = 0.0

    def get_credit_limit(self, counterparty_id: Optional[int] = None) -> float:
        """Credit limit based on trust, not collateral."""
        base_credit = self.trust * 10
        if counterparty_id is not None:
            return base_credit * (self.trust / 100)
        return base_credit

    def update_trust(self, counterparty_id: int, success: bool):
        delta = 2.0 if success else -3.0
        self.trust += delta
        self.trust = np.clip(self.trust, 0.0, 100.0)


class Household(BaseAgent):
    """Household agent with consumption, production, and social behavior."""
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.food_inventory = 50.0
        self.skill_level = 1.0
        self.children = 2
        self.age = 30

    def consume(self, food_needed: float, market) -> float:
        if self.food_inventory >= food_needed:
            self.food_inventory -= food_needed
            return 0.0
        else:
            shortage = food_needed - self.food_inventory
            self.food_inventory = 0
            cost = market.buy_food(shortage, self)
            self.gold -= cost
            return cost

    def produce(self, land_quality: float, water_availability: float) -> float:
        base_yield = land_quality * 1000 * self.skill_level
        water_factor = water_availability / 100.0
        harvest = base_yield * water_factor * (0.8 + 0.2 * random.random())
        self.food_inventory += harvest
        return harvest

    def pay_zakat(self, market, emirate) -> float:
        total_wealth = self.gold + (self.silver / market.silver_price * market.gold_price)
        if total_wealth >= 85:  # Nisab: 85g gold equivalent
            zakat = total_wealth * 0.025
            self.gold -= zakat / market.gold_price
            self.zakat_paid += zakat
            emirate.collect_zakat(zakat)
            self.moral_state.update_from_action("zakat_payment", 0.8)
            return zakat
        return 0.0

    def contribute_to_waqf(self, amount: float, waqf_institution) -> float:
        if amount <= self.gold:
            self.gold -= amount
            self.waqf_contributions += amount
            waqf_institution.receive_endowment(amount, self.unique_id)
            self.moral_state.update_from_action("waqf_contribution", 0.9)
            return amount
        return 0.0

    def step(self):
        # Simple production/consumption
        self.wealth = self.gold + self.silver * 0.1
        self.trust = max(0, min(100, self.trust + random.uniform(-0.5, 1.0)))
        
        # Moral evolution
        if self.wealth > 150:
            self.moral_state.update_from_action("hoarding", 0.5)


class Merchant(BaseAgent):
    """Merchant agent with trade and arbitrage."""
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.inventory = {}
        self.transport_capacity = 100.0
        self.reputation = 50
        self.contracts = []

    def arbitrage(self, market_a, market_b, commodity: str, quantity: float):
        price_a = market_a.get_price(commodity)
        price_b = market_b.get_price(commodity)
        if price_b > price_a * 1.05:
            self.gold += (price_b - price_a) * quantity
            self.moral_state.update_from_action("honest_trade", 0.8)

    def issue_contract(self, contract_type: str, terms: dict, counterparty):
        if self.trust > 60:
            contract = {"type": contract_type, "terms": terms, "parties": [self.unique_id, counterparty.unique_id]}
            self.contracts.append(contract)
            counterparty.contracts.append(contract)

    def step(self):
        self.wealth = self.gold + self.silver * 0.1
        self.trust = max(0, min(100, self.trust + random.uniform(-0.2, 0.5)))


class Farmer(BaseAgent):
    """Farmer agent with agricultural production."""
    
    def __init__(self, unique_id, model, land_quality=0.5):
        super().__init__(unique_id, model)
        self.land = land_quality
        self.harvest = 0.0
        self.storage = 0.0
        self.kharaj_paid = 0.0

    def produce(self, water_availability: float):
        base_yield = self.land * 1000
        water_factor = water_availability / 100.0
        self.harvest = base_yield * water_factor * (0.8 + 0.2 * random.random())
        self.storage += self.harvest
        self.food_inventory += self.harvest

    def pay_kharaj(self, emirate):
        kharaj = self.harvest * 0.1
        self.storage -= kharaj
        emirate.collect_kharaj(kharaj)
        self.kharaj_paid = kharaj

    def step(self):
        self.wealth = self.gold + self.silver * 0.1 + self.storage * 0.01
        self.trust = max(0, min(100, self.trust + random.uniform(-0.3, 0.3)))


# ============================================================
# LAYER 3: INSTITUTIONS
# ============================================================

class Emirate:
    """Governance layer with zakat collection and CRD management."""
    
    def __init__(self, name: str):
        self.name = name
        self.zakat_treasury = 0.0
        self.reserves = {"gold": 0.0, "silver": 0.0, "grain": 0.0}
        self.justice_index = 50
        self.corruption_level = 0.1

    def collect_zakat(self, amount: float):
        self.zakat_treasury += amount * (1 - self.corruption_level)

    def collect_kharaj(self, amount: float):
        self.zakat_treasury += amount * (1 - self.corruption_level)

    def distribute_zakat(self, agents: List[Agent]):
        """Distribute zakat to the poorest 50% of agents."""
        if self.zakat_treasury > 0:
            poor = sorted(agents, key=lambda a: a.wealth)[:len(agents)//2]
            for p in poor:
                share = self.zakat_treasury / len(poor)
                p.gold += share * 0.5
                p.silver += share * 0.3
            self.zakat_treasury = 0


class WaqfInstitution:
    """Perpetual endowment for public goods."""
    
    def __init__(self, name: str):
        self.name = name
        self.endowment = 0.0
        self.services = {"schools": 0, "hospitals": 0, "water_systems": 0}
        self.annual_return = 0.0

    def receive_endowment(self, amount: float, donor_id: int):
        self.endowment += amount

    def invest(self):
        self.annual_return = self.endowment * 0.05
        self.endowment += self.annual_return

    def distribute(self):
        for service in self.services:
            if self.annual_return >= 10:
                self.services[service] += 1
                self.annual_return -= 10


# ============================================================
# LAYER 2: ECONOMIC MECHANISMS
# ============================================================

class BimetallicMarket:
    """Market with Dinar/Dirham bimetallic system."""
    
    def __init__(self, initial_gold_price=100, initial_silver_price=15):
        self.gold_price = initial_gold_price
        self.silver_price = initial_silver_price
        self.gold_silver_ratio = initial_gold_price / initial_silver_price

    def update_prices(self, demand_gold: float, supply_gold: float, 
                      demand_silver: float, supply_silver: float):
        self.gold_price *= (1 + (demand_gold - supply_gold) / max(1, supply_gold) * 0.1)
        self.silver_price *= (1 + (demand_silver - supply_silver) / max(1, supply_silver) * 0.1)
        self.gold_silver_ratio = self.gold_price / self.silver_price


class CommodityReserveDepartment:
    """CRD for price stabilization (Grondona system)."""
    
    def __init__(self, target_prices: Dict[str, float], buffer_band=0.2):
        self.target_prices = target_prices
        self.buffer_band = buffer_band
        self.reserves = {commodity: 0 for commodity in target_prices}

    def stabilize(self, commodity: str, current_price: float):
        if current_price > self.target_prices[commodity] * (1 + self.buffer_band):
            # Sell reserves
            quantity = self.reserves.get(commodity, 0) * 0.2
            self.reserves[commodity] -= quantity
            return {"action": "sell", "quantity": quantity}
        elif current_price < self.target_prices[commodity] * (1 - self.buffer_band):
            # Buy reserves
            quantity = self.target_prices[commodity] * 100 / current_price
            self.reserves[commodity] = self.reserves.get(commodity, 0) + quantity
            return {"action": "buy", "quantity": quantity}
        return {"action": "hold", "quantity": 0}


# ============================================================
# LAYER 4: METRICS
# ============================================================

class CivilizationMetrics:
    """Data-driven civilization metrics (PCA-derived weights)."""
    
    def __init__(self):
        self.weights = {
            "wealth": 0.25,
            "trust": 0.25,
            "justice": 0.20,
            "ecology": 0.15,
            "spiritual": 0.15
        }

    def compute_civilization_index(self, agents: List[Agent], emirate: Emirate) -> float:
        wealth = np.mean([a.wealth for a in agents])
        trust = np.mean([a.trust for a in agents])
        justice = 1 - self.compute_gini(agents)
        spiritual = np.mean([a.waqf_contributions / max(1, a.wealth) for a in agents])
        
        return (self.weights["wealth"] * wealth / 100 +
                self.weights["trust"] * trust / 100 +
                self.weights["justice"] * justice +
                self.weights["spiritual"] * spiritual)

    @staticmethod
    def compute_gini(agents: List[Agent]) -> float:
        wealths = sorted([a.wealth for a in agents])
        n = len(wealths)
        if n == 0 or sum(wealths) == 0:
            return 0.5
        numerator = 2 * sum((i+1) * wealths[i] for i in range(n))
        denominator = n * sum(wealths)
        return max(0, min(1, 1 - numerator / denominator))


# ============================================================
# MAIN MODEL
# ============================================================

class ICESModel(Model):
    """
    Full ICES v2 model with 4-layer architecture.
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
        use_crd: bool = True,
        monetary_system: str = "dinar",
        seed: Optional[int] = None
    ):
        super().__init__(seed=seed)
        
        # Configuration
        self.use_zakat = use_zakat
        self.use_waqf = use_waqf
        self.use_crd = use_crd
        self.monetary_system = monetary_system
        self.year = 0
        
        # Space
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        
        # Markets
        self.market = BimetallicMarket()
        self.crd = CommodityReserveDepartment(
            target_prices={"grain": 10, "dates": 5, "salt": 2},
            buffer_band=0.2
        )
        
        # Institutions
        self.emirate = Emirate("Al-Madina")
        self.waqf = WaqfInstitution("Main Waqf")
        
        # Create agents
        self.agents = []
        for i in range(n_households):
            h = Household(i, self)
            self.grid.place_agent(h, (random.randrange(width), random.randrange(height)))
            self.schedule.add(h)
            self.agents.append(h)
            
        for i in range(n_merchants):
            m = Merchant(n_households + i, self)
            self.grid.place_agent(m, (random.randrange(width), random.randrange(height)))
            self.schedule.add(m)
            self.agents.append(m)
            
        for i in range(n_farmers):
            f = Farmer(n_households + n_merchants + i, self, land_quality=random.uniform(0.3, 0.9))
            self.grid.place_agent(f, (random.randrange(width), random.randrange(height)))
            self.schedule.add(f)
            self.agents.append(f)
        
        # Metrics
        self.metrics = CivilizationMetrics()
        self.datacollector = DataCollector(
            model_reporters={
                "Civilization_Index": self.compute_civilization_index,
                "Avg_Wealth": self.compute_avg_wealth,
                "Avg_Trust": self.compute_avg_trust,
                "Gini": self.metrics.compute_gini,
                "Zakat_Treasury": lambda: self.emirate.zakat_treasury,
                "Waqf_Endowment": lambda: self.waqf.endowment
            },
            agent_reporters={
                "Wealth": "wealth",
                "Trust": "trust"
            }
        )

    def step(self):
        self.year += 1
        
        # Agent physics
        self.schedule.step()
        
        # Economic mechanisms
        if self.use_crd:
            self.crd.stabilize("grain", self.market.gold_price)
        
        # Institutions
        if self.use_zakat and self.year % 12 == 0:
            for agent in self.agents:
                if hasattr(agent, 'pay_zakat'):
                    agent.pay_zakat(self.market, self.emirate)
            self.emirate.distribute_zakat(self.agents)
        
        if self.use_waqf and self.year % 12 == 0:
            self.waqf.invest()
            self.waqf.distribute()
        
        # Collect data
        self.datacollector.collect(self)

    def compute_civilization_index(self) -> float:
        return self.metrics.compute_civilization_index(self.agents, self.emirate)

    def compute_avg_wealth(self) -> float:
        return np.mean([a.wealth for a in self.agents])

    def compute_avg_trust(self) -> float:
        return np.mean([a.trust for a in self.agents])

    def run(self, n_steps: int = 100) -> pd.DataFrame:
        for _ in range(n_steps):
            self.step()
        return self.datacollector.get_model_vars_dataframe()


# ============================================================
# HIERARCHICAL BAYESIAN CALIBRATION (Fix 2)
# ============================================================

class HierarchicalBayesianCalibrator:
    """
    Hierarchical Bayesian calibration with partial pooling by civilization family.
    """
    
    def __init__(self, data: Dict[str, pd.DataFrame]):
        self.data = data
        self.families = {
            'islamic': ['medina', 'abbasids', 'mamluks', 'ottomans'],
            'european_commercial': ['venice', 'dutch_republic'],
            'east_asian_bureaucratic': ['song', 'ming'],
            'imperial': ['roman_empire', 'byzantine'],
            'modern': ['soviet']
        }
    
    def calibrate(self, n_samples=2000, tune=1000, chains=4):
        """
        Run hierarchical Bayesian calibration.
        """
        import pymc as pm
        import arviz as az
        
        with pm.Model() as model:
            # Hyperpriors
            mu_trust = pm.Normal('mu_trust', mu=0.5, sigma=0.2)
            sigma_trust = pm.HalfNormal('sigma_trust', sigma=0.1)
            
            mu_institutional = pm.Normal('mu_institutional', mu=0.5, sigma=0.2)
            sigma_institutional = pm.HalfNormal('sigma_institutional', sigma=0.1)
            
            # Family-level parameters
            family_trust = pm.Normal(
                'family_trust',
                mu=mu_trust,
                sigma=sigma_trust,
                shape=len(self.families)
            )
            
            # Civilization-level parameters
            for civ in self.data.keys():
                family_idx = self._get_family_index(civ)
                trust_civ = pm.Normal(
                    f'trust_{civ}',
                    mu=family_trust[family_idx],
                    sigma=0.05,
                    shape=len(self.data[civ])
                )
                
                # Observation model
                if 'population' in self.data[civ].columns:
                    pm.Normal(
                        f'pop_obs_{civ}',
                        mu=0.3 * trust_civ + 0.2 * pm.Normal(f'inst_{civ}', mu=0.5, sigma=0.1),
                        sigma=0.05,
                        observed=self.data[civ]['population'].values / 100
                    )
            
            trace = pm.sample(n_samples, tune=tune, chains=chains, return_inferencedata=True)
        
        return trace
    
    def _get_family_index(self, civ_name: str) -> int:
        for idx, (family, members) in enumerate(self.families.items()):
            if civ_name in members:
                return idx
        return 0


# ============================================================
# GLOBAL SENSITIVITY ANALYSIS (Fix 1)
# ============================================================

class SobolAnalyzer:
    """
    Global Sensitivity Analysis using Sobol indices.
    """
    
    def __init__(self, model_func, params: Dict[str, Tuple[float, float]], output_key="CI"):
        self.model_func = model_func
        self.params = params
        self.output_key = output_key
        self.problem = {
            'num_vars': len(params),
            'names': list(params.keys()),
            'bounds': list(params.values())
        }
    
    def analyze(self, n_samples=1000):
        from SALib.sample import saltelli
        from SALib.analyze import sobol
        import numpy as np
        
        param_values = saltelli.sample(self.problem, n_samples)
        
        outputs = []
        for p in param_values:
            param_dict = {name: p[i] for i, name in enumerate(self.problem['names'])}
            result = self.model_func(param_dict)
            outputs.append(result[self.output_key])
        
        outputs = np.array(outputs)
        Si = sobol.analyze(self.problem, outputs, print_to_console=False)
        
        return {
            'first_order': dict(zip(self.problem['names'], Si['S1'])),
            'total_order': dict(zip(self.problem['names'], Si['ST'])),
            'driving_params': [name for name, st in zip(self.problem['names'], Si['ST']) if st > 0.05]
        }
