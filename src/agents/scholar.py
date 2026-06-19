# src/agents/scholar.py
"""
Scholar agent for Sharia council and adaptive jurisprudence.
"""

import random
from typing import Dict, List

class Scholar:
    """Scholar agent with legal expertise and adaptive ijtihad."""
    
    def __init__(self, unique_id: int, name: str = None):
        self.unique_id = unique_id
        self.name = name or f"Scholar_{unique_id}"
        self.expertise = {
            "fiqh": random.uniform(0.5, 1.0),
            "usul": random.uniform(0.5, 1.0),
            "hadith": random.uniform(0.5, 1.0),
            "tafsir": random.uniform(0.5, 1.0)
        }
        self.opinions = {}
        self.reputation = 50
        self.school = random.choice(["Maliki", "Hanafi", "Shafii", "Hanbali"])

    def issue_opinion(self, issue: str, context: Dict) -> Dict:
        """Issue a legal opinion (fatwa) based on ijtihad."""
        if issue in self.opinions:
            return self.opinions[issue]
        
        # Use qiyas (analogical reasoning) and maslaha (public interest)
        if issue == "AI_economy":
            opinion = {
                "ruling": "permissible",
                "condition": "AI-generated wealth is subject to zakat",
                "reasoning": "qiyas on trade profits",
                "scholar": self.name
            }
        elif issue == "pandemic":
            opinion = {
                "ruling": "permissible",
                "condition": "Zakat can be used for healthcare",
                "reasoning": "maslaha (public interest)",
                "scholar": self.name
            }
        elif issue == "cryptocurrency":
            opinion = {
                "ruling": "conditional",
                "condition": "Permissible if backed by real assets",
                "reasoning": "ijtihad on new financial instruments",
                "scholar": self.name
            }
        else:
            opinion = {
                "ruling": "pending",
                "condition": "requires further study",
                "reasoning": "istishab (presumption of permissibility)",
                "scholar": self.name
            }
        
        self.opinions[issue] = opinion
        return opinion

    def adapt_jurisprudence(self, novel_condition: str):
        """Adapt legal framework to novel conditions."""
        # Ijtihad: independent reasoning
        if novel_condition in ["AI_economy", "cyber_warfare", "climate_shock"]:
            self.expertise["fiqh"] += 0.05
            self.expertise["usul"] += 0.03
            self.reputation += 5
            return {"adapted": True, "condition": novel_condition}
        return {"adapted": False, "reason": "Condition not recognized"}

    def to_dict(self) -> Dict:
        return {
            "id": self.unique_id,
            "name": self.name,
            "expertise": self.expertise,
            "reputation": self.reputation,
            "school": self.school,
            "opinions": len(self.opinions)
        }
