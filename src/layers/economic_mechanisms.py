# src/layers/economic_mechanisms.py
"""
Layer 2: Economic Mechanisms - How exchanges occur.
"""

import numpy as np
from typing import Dict, Optional

class BimetallicMarket:
    """Bimetallic market with Dinar and Dirham."""
    
    def __init__(self, initial_gold_price: float = 100.0, initial_silver_price: float = 15.0):
        self.gold_price = initial_gold_price
        self.silver_price = initial_silver_price
        self.gold_silver_ratio = initial_gold_price / initial_silver_price
        self.price_level = 100.0
        self.history = []

    def update_prices(self, demand_gold: float, supply_gold: float, 
                      demand_silver: float, supply_silver: float):
        """Update prices based on supply and demand."""
        self.gold_price *= (1 + (demand_gold - supply_gold) / max(1, supply_gold) * 0.1)
        self.silver_price *= (1 + (demand_silver - supply_silver) / max(1, supply_silver) * 0.1)
        self.gold_silver_ratio = self.gold_price / self.silver_price
        
        # Update price level (weighted by gold and silver)
        self.price_level = (self.gold_price * 0.6 + self.silver_price * 0.4) / 100.0
        
        self.history.append({
            "gold_price": self.gold_price,
            "silver_price": self.silver_price,
            "ratio": self.gold_silver_ratio,
            "price_level": self.price_level
        })

    def get_price(self, commodity: str) -> float:
        """Get price for a commodity."""
        if commodity == "grain":
            return self.gold_price * 0.1
        elif commodity == "dates":
            return self.gold_price * 0.05
        elif commodity == "salt":
            return self.gold_price * 0.02
        elif commodity == "copper":
            return self.silver_price * 0.5
        return self.gold_price * 0.1

    def buy_food(self, quantity: float, buyer) -> float:
        """Buy food from the market."""
        price_per_unit = self.get_price("grain")
        total_cost = price_per_unit * quantity
        if buyer.gold >= total_cost:
            buyer.gold -= total_cost
            return total_cost
        return 0.0


class CommodityReserveDepartment:
    """Commodity Reserve Department (CRD) for price stabilization."""
    
    def __init__(self, target_prices: Dict[str, float] = None, buffer_band: float = 0.2):
        if target_prices is None:
            target_prices = {"grain": 10, "dates": 5, "salt": 2}
        self.target_prices = target_prices
        self.buffer_band = buffer_band
        self.reserves = {commodity: 0 for commodity in target_prices}
        self.history = []

    def stabilize(self, commodity: str, current_price: float) -> Dict:
        """Stabilize price by buying or selling reserves."""
        if commodity not in self.target_prices:
            return {"action": "hold", "quantity": 0}
        
        target = self.target_prices[commodity]
        upper = target * (1 + self.buffer_band)
        lower = target * (1 - self.buffer_band)
        
        if current_price > upper:
            # Sell reserves to lower price
            quantity = self.reserves.get(commodity, 0) * 0.2
            self.reserves[commodity] = self.reserves.get(commodity, 0) - quantity
            action = "sell"
        elif current_price < lower:
            # Buy reserves to raise price
            quantity = target * 100 / current_price
            self.reserves[commodity] = self.reserves.get(commodity, 0) + quantity
            action = "buy"
        else:
            quantity = 0
            action = "hold"
        
        self.history.append({
            "commodity": commodity,
            "action": action,
            "quantity": quantity,
            "price": current_price,
            "target": target
        })
        
        return {"action": action, "quantity": quantity}


class EconomicMechanisms:
    """Layer 2: Economic Mechanisms."""
    
    def __init__(self, monetary_system: str = "dinar", use_crd: bool = True):
        self.monetary_system = monetary_system
        self.use_crd = use_crd
        self.market = BimetallicMarket()
        self.crd = CommodityReserveDepartment()
        self.price_level = 100.0
        self.money_supply = 1000.0
        self.transaction_volume = 0.0
        self.history = []

    def step(self, agents: list):
        """Execute one time step for economic mechanisms."""
        # Compute aggregate supply and demand
        total_gold = sum(getattr(a, 'gold', 0) for a in agents)
        total_silver = sum(getattr(a, 'silver', 0) for a in agents)
        total_food = sum(getattr(a, 'food_inventory', 0) for a in agents)
        
        # Update market prices
        demand_gold = total_gold * 0.1
        supply_gold = total_gold * 0.05
        demand_silver = total_silver * 0.1
        supply_silver = total_silver * 0.05
        
        self.market.update_prices(demand_gold, supply_gold, demand_silver, supply_silver)
        
        # CRD stabilization
        if self.use_crd:
            grain_price = self.market.get_price("grain
