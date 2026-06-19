# src/agents/farmer.py
"""
Farmer agent with agricultural production and kharaj payment.
"""

import random
from .base import BaseAgent

class Farmer(BaseAgent):
    """Farmer agent with agricultural production."""
    
    def __init__(self, unique_id: int, model, initial_wealth: float = 30.0, land_quality: float = 0.5):
        super().__init__(unique_id, model, initial_wealth)
        self.land = land_quality
        self.harvest = 0.0
        self.storage = 0.0
        self.kharaj_paid = 0.0
        self.debt_to_deliver = 0.0
        self.delivery_date = 0

    def produce(self, weather_factor: float = 1.0, water_availability: float = 100.0):
        """Produce agricultural output."""
        base_yield = self.land * 1000
        water_factor = water_availability / 100.0
        weather = 0.8 + 0.2 * weather_factor
        self.harvest = base_yield * water_factor * weather * (0.8 + 0.2 * random.random())
        self.storage += self.harvest
        self.food_inventory += self.harvest

    def pay_kharaj(self, emirate) -> float:
        """Pay land tax (kharaj)."""
        kharaj = self.harvest * 0.1
        self.storage -= kharaj
        emirate.collect_kharaj(kharaj)
        self.kharaj_paid = kharaj
        return kharaj

    def store_grain(self, amount: float):
        """Store grain in reserves (Yusuf-style)."""
        if self.storage >= amount:
            self.storage -= amount
            return amount
        return 0.0

    def release_grain(self, amount: float) -> float:
        """Release grain from reserves during scarcity."""
        release = min(amount, self.storage)
        self.storage -= release
        return release

    def step(self):
        """Execute one time step for the farmer."""
        self.wealth = self.gold + self.silver * 0.1 + self.storage * 0.01
        
        # Produce based on ecology
        water = self.model.agent_physics.water_availability if hasattr(self.model, 'agent_physics') else 100
        weather = self.model.agent_physics.weather_factor if hasattr(self.model, 'agent_physics') else 1.0
        self.produce(weather, water)
        
        # Pay kharaj annually
        if self.model.year % 12 == 0:
            self.pay_kharaj(self.model.emirate)
        
        # Trust evolves
        self.trust += random.uniform(-0.3, 0.3)
        self.trust = np.clip(self.trust, 0.0, 100.0)
