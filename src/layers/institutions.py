# src/layers/institutions.py
"""
Layer 3: Institutions - How behavior is constrained and incentivized.
"""

from typing import List, Dict, Optional
from src.agents.waqf import WaqfInstitution
from src.agents.emir import Emirate
from src.agents.scholar import Scholar

class InstitutionalLayer:
    """Layer 3: Institutions."""
    
    def __init__(self, use_zakat: bool = True, use_waqf: bool = True, use_hisba: bool = True):
        self.use_zakat = use_zakat
        self.use_waqf = use_waqf
        self.use_hisba = use_hisba
        self.emirate = None
        self.waqf = None
        self.scholars = []
        self.hisba_cases = []

    def initialize(self, name: str = "Al-Madina"):
        """Initialize institutions."""
        self.emirate = Emirate(name)
        self.waqf = WaqfInstitution(f"{name} Waqf")
        self.scholars = [Scholar(i) for i in range(5)]

    def step(self, agents: List, year: int):
        """Execute one time step for institutions."""
        if self.emirate is None:
            self.initialize()
        
        # Zakat collection and distribution
        if self.use_zakat and year % 12 == 0:
            for agent in agents:
                if hasattr(agent, 'pay_zakat'):
                    agent.pay_zakat(self.emirate.market, self.emirate)
            self.emirate.distribute_zakat(agents)
        
        # Waqf management
        if self.use_waqf and year % 12 == 0:
            self.waqf.invest()
            self.waqf.distribute()
        
        # Hisba market supervision
        if self.use_hisba and year % 6 == 0:
            self.hisba_supervision(agents)
        
        # Update justice index
        self.emirate.update_justice(agents)

    def hisba_supervision(self, agents: List):
        """Supervise markets and punish fraud."""
        for agent in agents:
            # Detect hoarding
            if hasattr(agent, 'food_inventory') and agent.food_inventory > 100:
                self.hisba_cases.append({
                    "agent": agent.unique_id,
                    "offense": "hoarding",
                    "penalty": 0.05 * agent.wealth,
                    "year": len(self.hisba_cases)
                })
                agent.wealth *= 0.95
                agent.trust -= 10
            
            # Detect fraud
            if hasattr(agent, 'contracts'):
                for contract in agent.contracts:
                    if contract.get("status") == "failed":
                        self.hisba_cases.append({
                            "agent": agent.unique_id,
                            "offense": "fraud",
                            "penalty": 0.1 * agent.wealth,
                            "year": len(self.hisba_cases)
                        })
                        agent.wealth *= 0.9
                        agent.trust -= 20

    def to_dict(self) -> Dict:
        return {
            "use_zakat": self.use_zakat,
            "use_waqf": self.use_waqf,
            "use_hisba": self.use_hisba,
            "emirate": self.emirate.to_dict() if self.emirate else None,
            "waqf": self.waqf.to_dict() if self.waqf else None,
            "scholars": [s.to_dict() for s in self.scholars],
            "hisba_cases": len(self.hisba_cases)
        }
