# src/models/ices_model.py
"""
ICES v2 - Islamic Civilizational Economic Simulator
Main model class with 4-layer architecture.
"""

import numpy as np
import networkx as nx
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random

class MinimalICESModel(Model):
    """
    Simplified version of ICES v2 for initial implementation.
    Full version includes hierarchical Bayesian calibration and all 4 layers.
    """

    def __init__(self, n_agents=50, use_zakat=True, use_waqf=True, 
                 use_crd=True, monetary_system="dinar", seed=None):
        super().__init__(seed=seed)
        self.num_agents = n_agents
        self.use_zakat = use_zakat
        self.use_waqf = use_waqf
        self.use_crd = use_crd
        self.monetary_system = monetary_system
        
        self.grid = MultiGrid(10, 10, torus=False)
        self.schedule = RandomActivation(self)
        self.year = 0
        
        # Create agents
        for i in range(self.num_agents):
            agent = SelfAgent(i, self)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)
        
        # Data collector
        self.datacollector = DataCollector(
            model_reporters={
                "Avg_Wealth": self.compute_avg_wealth,
                "Avg_Trust": self.compute_avg_trust,
                "Gini": self.compute_gini,
            }
        )

    def step(self):
        self.year += 1
        self.schedule.step()
        self.datacollector.collect(self)
        
        if self.use_zakat and self.year % 12 == 0:
            self.apply_zakat()

    def apply_zakat(self):
        # Simplified zakat
        nisab = 85
        for agent in self.schedule.agents:
            if agent.wealth >= nisab:
                zakat = agent.wealth * 0.025
                agent.wealth -= zakat
                poor = sorted(self.schedule.agents, key=lambda a: a.wealth)[:self.num_agents//2]
                for p in poor:
                    p.wealth += zakat / len(poor)

    def compute_avg_wealth(self):
        return np.mean([a.wealth for a in self.schedule.agents])

    def compute_avg_trust(self):
        return np.mean([a.trust for a in self.schedule.agents])

    def compute_gini(self):
        wealths = sorted([a.wealth for a in self.schedule.agents])
        n = len(wealths)
        if n == 0 or sum(wealths) == 0:
            return 0.5
        numerator = 2 * sum((i+1) * wealths[i] for i in range(n))
        denominator = n * sum(wealths)
        return max(0, min(1, 1 - numerator / denominator))

    def run(self, n_steps=100):
        for _ in range(n_steps):
            self.step()
        return self.datacollector.get_model_vars_dataframe()


class SelfAgent(Agent):
    """Minimal agent for ICES v2."""
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = random.uniform(10, 100)
        self.trust = random.uniform(20, 80)
        self.moral_state = {"taqwa": 0.5, "greed": 0.5}

    def step(self):
        self.wealth += random.uniform(-2, 5)
        self.trust = max(0, min(100, self.trust + random.uniform(-1, 2)))
        if self.wealth > 150:
            self.moral_state["greed"] += 0.01
        else:
            self.moral_state["taqwa"] += 0.01
