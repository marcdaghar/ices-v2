# src/agents/base.py
"""
Base agent class with trust, wealth, and moral state.
"""

import numpy as np
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class MoralState:
    """Endogenous moral formation through reinforcement learning."""
    taqwa: float = 0.5
    greed: float = 0.5
    solidarity: float = 0.5
    trustworthiness: float = 0.5

    def update_from_action(self, action: str, outcome: float):
        """
        Morality emerges from experience, not direct assignment.
        This prevents circularity: moral states are learned, not imposed.
        """
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

    def to_dict(self) -> Dict:
        return {
            "taqwa": self.taqwa,
            "greed": self.greed,
            "solidarity": self.solidarity,
            "trustworthiness": self.trustworthiness
        }


class BaseAgent:
    """Base agent class for all ICES agents."""
    
    def __init__(self, unique_id: int, model, initial_wealth: float = 50.0):
        self.unique_id = unique_id
        self.model = model
        self.wealth = initial_wealth
        self.gold = initial_wealth * 0.4
        self.silver = initial_wealth * 0.3
        self.trust = random.uniform(20, 80)
        self.moral_state = MoralState()
        self.history = []
        self.zakat_paid = 0.0
        self.waqf_contributions = 0.0
        self.location = (random.randint(0, model.grid.width - 1), 
                         random.randint(0, model.grid.height - 1))

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
        self.moral_state.update_from_action(
            "honest_trade" if success else "fraud",
            0.8 if success else 0.2
        )

    def to_dict(self) -> Dict:
        return {
            "id": self.unique_id,
            "wealth": self.wealth,
            "gold": self.gold,
            "silver": self.silver,
            "trust": self.trust,
            "moral_state": self.moral_state.to_dict(),
            "zakat_paid": self.zakat_paid,
            "waqf_contributions": self.waqf_contributions
        }
