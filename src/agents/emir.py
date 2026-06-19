# src/agents/emir.py
"""
Emirate agent for governance, zakat collection, and CRD management.
"""

from typing import Dict, List

class Emirate:
    """Governance layer with zakat collection and CRD management."""
    
    def __init__(self, name: str = "Al-Madina"):
        self.name = name
        self.zakat_treasury = 0.0
        self.kharaj_treasury = 0.0
        self.reserves = {
            "gold": 0.0,
            "silver": 0.0,
            "grain": 0.0,
            "strategic_commodities": {}
        }
        self.justice_index = 50
        self.corruption_level = 0.1
        self.history = []

    def collect_zakat(self, amount: float):
        """Collect zakat with corruption discount."""
        collected = amount * (1 - self.corruption_level)
        self.zakat_treasury += collected
        self.history.append({"type": "zakat", "amount": collected})

    def collect_kharaj(self, amount: float):
        """Collect kharaj (land tax)."""
        self.kharaj_treasury += amount
        self.history.append({"type": "kharaj", "amount": amount})

    def distribute_zakat(self, agents: List, poor_ratio: float = 0.5):
        """Distribute zakat to the poorest agents."""
        if self.zakat_treasury <= 0:
            return
        
        poor = sorted(agents, key=lambda a: a.wealth)[:int(len(agents) * poor_ratio)]
        if not poor:
            return
        
        share = self.zakat_treasury / len(poor)
        for p in poor:
            p.gold += share * 0.5
            p.silver += share * 0.3
            p.wealth += share
        
        self.history.append({"type": "distribution", "amount": self.zakat_treasury})
        self.zakat_treasury = 0

    def manage_crd(self, commodity: str, current_price: float, target_price: float, buffer_band: float = 0.2):
        """
        Manage Commodity Reserve Department (Grondona system).
        """
        if commodity not in self.reserves["strategic_commodities"]:
            self.reserves["strategic_commodities"][commodity] = 0
        
        if current_price > target_price * (1 + buffer_band):
            # Sell reserves
            quantity = self.reserves["strategic_commodities"][commodity] * 0.2
            self.reserves["strategic_commodities"][commodity] -= quantity
            return {"action": "sell", "quantity": quantity}
        elif current_price < target_price * (1 - buffer_band):
            # Buy reserves
            quantity = target_price * 100 / current_price
            self.reserves["strategic_commodities"][commodity] += quantity
            return {"action": "buy", "quantity": quantity}
        return {"action": "hold", "quantity": 0}

    def update_justice(self, agents: List):
        """Update justice index based on inequality and market access."""
        # Gini coefficient
        wealths = sorted([a.wealth for a in agents])
        n = len(wealths)
        if n > 0 and sum(wealths) > 0:
            numerator = 2 * sum((i+1) * wealths[i] for i in range(n))
            denominator = n * sum(wealths)
            gini = 1 - numerator / denominator
            self.justice_index = 100 * (1 - gini)
        
        # Corruption reduces justice
        self.justice_index *= (1 - self.corruption_level)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "zakat_treasury": self.zakat_treasury,
            "kharaj_treasury": self.kharaj_treasury,
            "reserves": self.reserves,
            "justice_index": self.justice_index,
            "corruption_level": self.corruption_level
        }
