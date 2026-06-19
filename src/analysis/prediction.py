# src/analysis/prediction.py
"""
Out-of-Sample Prediction Protocol.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Callable, Any

class PredictionProtocol:
    """
    Formal out-of-sample prediction protocol.
    """
    
    def __init__(self, model: Callable, data: Dict[str, pd.DataFrame], observed_var: str = "population"):
        self.model = model
        self.data = data
        self.observed_var = observed_var

    def split_data(self, civilization: str, train_ratio: float = 0.7, predict_ratio: float = 0.15) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Split data into train, predict, and test sets."""
        df = self.data[civilization]
        n = len(df)
        train_end = int(n * train_ratio)
        predict_end = train_end + int(n * predict_ratio)
        return df.iloc[:train_end], df.iloc[train_end:predict_end], df.iloc[predict_end:]

    def run(self, civilization: str, n_sims: int = 100) -> Dict[str, Any]:
        """Run prediction protocol."""
        train, predict, test = self.split_data(civilization)
        self.model.calibrate(train)
        
        predictions = []
        for _ in range(n_sims):
            pred = self.model.predict(predict["year"])
            predictions.append(pred[self.observed_var])
        predictions = np.array(predictions)
        
        pred_mean = np.mean(predictions, axis=0)
        pred_std = np.std(predictions, axis=0)
        actual = predict[self.observed_var].values
        
        rmse = np.sqrt(np.mean((pred_mean - actual) ** 2))
        within_95ci = np.mean((actual >= pred_mean - 1.96 * pred_std) & (actual <= pred_mean + 1.96 * pred_std))
        
        return {
            "civilization": civilization,
            "rmse": rmse,
            "within_95ci": within_95ci,
            "success": rmse < 0.15 and within_95ci > 0.9
        }
