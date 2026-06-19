# src/agents/merchant.py
"""
Merchant agent with trade, arbitrage, and contracts.
"""

import random
from .base import BaseAgent

class Merchant(BaseAgent):
    """Merchant agent with trade and arbitrage."""
    
    def __init__(self, unique_id: int, model, initial_wealth: float = 100.0):
        super().__init__(unique_id, model, initial_wealth)
        self.inventory = {}
        self.transport_capacity = 100.0
        self.reputation = 50
        self.contracts = []
        self.trade_routes = []

    def arbitrage(self, market_a, market_b, commodity: str, quantity: float):
        """Execute arbitrage between two markets."""
        price_a = market_a.get_price(commodity)
        price_b = market_b.get_price(commodity)
        if price_b > price_a * 1.05:
            profit = (price_b - price_a) * quantity
            self.gold += profit
            self.wealth += profit
            self.moral_state.update_from_action("honest_trade", 0.8)
            return {"success": True, "profit": profit}
        return {"success": False, "reason": "No arbitrage opportunity"}

    def issue_contract(self, contract_type: str, terms: dict, counterparty) -> Dict:
        """Issue an Islamic contract (Murabaha, Salam, Ijara, etc.)."""
        if self.trust < 60:
            return {"success": False, "reason": "Insufficient trust"}
        
        contract = {
            "type": contract_type,
            "terms": terms,
            "parties": [self.unique_id, counterparty.unique_id],
            "interest": 0,  # Riba is forbidden
            "status": "pending"
        }
        self.contracts.append(contract)
        counterparty.contracts.append(contract)
        return {"success": True, "contract": contract}

    def murabaha(self, cost: float, margin: float, buyer) -> Dict:
        """Cost-plus sale with deferred payment."""
        price = cost * (1 + margin)
        if buyer.trust >= 50:
            buyer.gold -= price
            self.gold += price
            self.wealth += price
            return {"success": True, "price": price, "margin": margin}
        return {"success": False, "reason": "Buyer trust insufficient"}

    def salam(self, quantity: float, price: float, delivery_date: int, farmer) -> Dict:
        """Forward agricultural contract."""
        if farmer.trust >= 40:
            farmer.gold += price
            self.gold -= price
            farmer.debt_to_deliver = quantity
            farmer.delivery_date = delivery_date
            return {"success": True, "quantity": quantity, "price": price}
        return {"success": False, "reason": "Farmer trust insufficient"}

    def step(self):
        """Execute one time step for the merchant."""
        self.wealth = self.gold + self.silver * 0.1
        
        # Update trust
        self.trust += random.uniform(-0.2, 0.5)
        self.trust = np.clip(self.trust, 0.0, 100.0)
        
        # Reputation evolves with successful trades
        successful_trades = sum(1 for c in self.contracts if c.get("status") == "completed")
        if successful_trades > len(self.contracts) * 0.7:
            self.reputation += 1
        else:
            self.reputation -= 1
        self.reputation = np.clip(self.reputation, 0, 100)
