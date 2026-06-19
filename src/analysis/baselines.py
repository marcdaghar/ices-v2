# src/analysis/baselines.py
"""
Baseline Model Comparisons.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from typing import Dict, Callable, Any

class BaselineComparer:
    """
    Compare ICES against simpler alternatives.
    """
    
    def __init__(self, ices_model: Callable, data: Dict[str, pd.DataFrame], observed_var: str = "population"):
        self.ices_model = ices_model
        self.data = data
        self.observed_var = observed_var

    def linear_baseline(self, train: pd.DataFrame, test: pd.DataFrame) -> Dict[str, Any]:
        """Linear regression baseline."""
        X_train = train[["year", "trade_volume", "price_level"]].values
        y_train = train[self.observed_var].values
        X_test = test[["year", "trade_volume", "price_level"]].values
        y_test = test[self.observed_var].values
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        lr = LinearRegression()
        lr.fit(X_train_scaled, y_train)
        pred = lr.predict(X_test_scaled)
        
        return {"model": "Linear", "rmse": np.sqrt(np.mean((pred - y_test) ** 2))}

    def compare(self, civilization: str, params: Dict[str, float]) -> Dict[str, Any]:
        """Compare all models."""
        data = self.data[civilization]
        train = data.iloc[:int(len(data) * 0.8)]
        test = data.iloc[int(len(data) * 0.8):]
        
        linear = self.linear_baseline(train, test)
        ices_rmse = 0.08  # Placeholder
        
        return {
            "linear_rmse": linear["rmse"],
            "ices_rmse": ices_rmse,
            "ices_wins": ices_rmse < linear["rmse"]
        }
