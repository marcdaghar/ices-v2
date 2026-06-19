# src/__init__.py
"""
ICES v2 - Islamic Civilizational Economic Simulator
"""

from src.models.ices_model import ICESModel, ICESExperimentRunner
from src.agents import Household, Merchant, Farmer, WaqfInstitution, Scholar, Emirate
from src.layers import AgentPhysics, EconomicMechanisms, InstitutionalLayer, MetricsLayer
from src.analysis import (
    SobolAnalyzer,
    HierarchicalBayesianCalibrator,
    FalsifiabilityTester,
    PredictionProtocol,
    BaselineComparer,
    MinimumPublishableCore
)

__version__ = "2.0.0"
__author__ = "Marc Gilbert Daghar"

__all__ = [
    "ICESModel",
    "ICESExperimentRunner",
    "Household",
    "Merchant",
    "Farmer",
    "WaqfInstitution",
    "Scholar",
    "Emirate",
    "AgentPhysics",
    "EconomicMechanisms",
    "InstitutionalLayer",
    "MetricsLayer",
    "SobolAnalyzer",
    "HierarchicalBayesianCalibrator",
    "FalsifiabilityTester",
    "PredictionProtocol",
    "BaselineComparer",
    "MinimumPublishableCore"
]
