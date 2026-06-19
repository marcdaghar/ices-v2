# src/agents/household.py
"""
Household agent with consumption, production, and social behavior.
"""

import numpy as np
import random
from .base import BaseAgent

class Household(BaseAgent):
    """Household agent with consumption, production, and social behavior."""
    
    def __init__(self, unique_id: int, model, initial_wealth: float = 50.0):
        super().__init__(unique_id, model, initial_wealth)
        self.food_inventory = 50.0
        self.skill_level = 1.0
        self.children = random.randint(1, 4)
        self.age = random.randint(18, 60)
        self.land_quality = random.uniform(0.3, 0.9)

    def consume(self, food_needed: float, market) -> float:
        """Consume food; if insufficient, purchase from market."""
        if self.food_inventory >= food_needed:
            self.food_inventory -= food_needed
            return 0.0
        else:
            shortage = food_needed - self.food_inventory
            self.food_inventory = 0
            cost = market.buy_food(shortage, self)
            self.gold -= cost
            self.wealth -= cost
            return cost

    def produce(self, water_availability: float) -> float:
        """Produce food based on land quality, water, and skill."""
        base_yield = self.land_quality * 1000 * self.skill_level
        water_factor = water_availability / 100.0
        harvest = base_yield * water_factor * (0.8 + 0.2 * random.random())
        self.food_inventory += harvest
        return harvest

    def pay_zakat(self, market, emirate) -> float:
        """Calculate and pay zakat on wealth."""
        total_wealth = self.gold + (self.silver / market.silver_price * market.gold_price)
        nisab = 85  # 85g gold equivalent
        if total_wealth >= nisab:
            zakat = total_wealth * 0.025
            self.gold -= zakat / market.gold_price
            self.zakat_paid += zakat
            emirate.collect_zakat(zakat)
            self.moral_state.update_from_action("zakat_payment", 0.8)
            return zakat
        return 0.0

    def contribute_to_waqf(self, amount: float, waqf_institution) -> float:
        """Contribute to a waqf endowment."""
        if amount <= self.gold:
            self.gold -= amount
            self.waqf_contributions += amount
            waqf_institution.receive_endowment(amount, self.unique_id)
            self.moral_state.update_from_action("waqf_contribution", 0.9)
            return amount
        return 0.0

    def trade(self, other_agent, commodity: str, quantity: float, market, trust_network) -> Dict:
        """Trade goods with another agent."""
        if self.trust < 30 or other_agent.trust < 30:
            return {"success": False, "reason": "Insufficient trust"}

        price = market.get_price(commodity)
        
        if self.gold >= price * quantity:
            self.gold -= price * quantity
            other_agent.gold += price * quantity
            self.moral_state.update_from_action("honest_trade", 0.8)
            other_agent.moral_state.update_from_action("honest_trade", 0.8)
            trust_network.update_trust(self.unique_id, other_agent.unique_id, success=True)
            return {"success": True, "price": price, "quantity": quantity}
        else:
            return {"success": False, "reason": "Insufficient gold"}

    def step(self):
        """Execute one time step for the household."""
        self.wealth = self.gold + self.silver * 0.1 + self.food_inventory * 0.01
        
        # Simple production
        water = self.model.agent_physics.water_availability
        self.produce(water)
        
        # Consumption
        food_needed = 2 + 0.5 * self.children
        self.consume(food_needed, self.model.economic.market)
        
        # Trust evolves with interactions
        self.trust += random.uniform(-0.5, 1.0)
        self.trust = np.clip(self.trust, 0.0, 100.0)
        
        # Moral evolution
        if self.wealth > 150:
            self.moral_state.update_from_action("hoarding", 0.5)
