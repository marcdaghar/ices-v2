# src/agents/waqf.py
"""
Waqf institution for perpetual endowments.
"""

from typing import Dict, List

class WaqfInstitution:
    """Perpetual endowment for public goods."""
    
    def __init__(self, name: str = "Main Waqf"):
        self.name = name
        self.endowment = 0.0
        self.services = {
            "schools": 0,
            "hospitals": 0,
            "water_systems": 0,
            "mosques": 0,
            "roads": 0
        }
        self.annual_return = 0.0
        self.history = []
        self.donors = {}

    def receive_endowment(self, amount: float, donor_id: int):
        """Receive a new endowment."""
        self.endowment += amount
        self.donors[donor_id] = self.donors.get(donor_id, 0) + amount
        self.history.append({
            "type": "endowment",
            "amount": amount,
            "donor": donor_id,
            "year": len(self.history)
        })

    def invest(self, return_rate: float = 0.05):
        """Invest endowment in productive assets."""
        self.annual_return = self.endowment * return_rate
        self.endowment += self.annual_return

    def distribute(self, costs: Dict[str, float] = None):
        """Distribute returns to services."""
        if costs is None:
            costs = {
                "schools": 10,
                "hospitals": 15,
                "water_systems": 8,
                "mosques": 5,
                "roads": 12
            }
        
        remaining = self.annual_return
        for service, cost in costs.items():
            if remaining >= cost:
                self.services[service] += 1
                remaining -= cost
                self.history.append({
                    "type": "service",
                    "service": service,
                    "amount": cost,
                    "year": len(self.history)
                })
            else:
                break

    def get_service_count(self, service: str) -> int:
        return self.services.get(service, 0)

    def total_services(self) -> int:
        return sum(self.services.values())

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "endowment": self.endowment,
            "annual_return": self.annual_return,
            "services": self.services,
            "total_services": self.total_services(),
            "donors": len(self.donors)
        }
