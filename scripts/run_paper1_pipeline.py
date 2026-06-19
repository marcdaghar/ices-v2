# scripts/run_paper1_pipeline.py
"""
Complete pipeline for ICES v2 Paper 1.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from src.models.ices_model import MinimalICESModel

def run_pipeline():
    print("="*60)
    print("ICES v2 PAPER 1 PIPELINE")
    print("="*60)
    
    # Run simulation
    print("\n[1] Running simulation...")
    model = MinimalICESModel(n_agents=50, use_zakat=True, use_waqf=True, use_crd=True)
    df = model.run(n_steps=100)
    
    # Save results
    print("\n[2] Saving results...")
    df.to_csv("results/paper1/simulation_results.csv", index=False)
    
    print("\n[3] Summary:")
    print(f"    Final Avg Wealth: {df['Avg_Wealth'].iloc[-1]:.1f}")
    print(f"    Final Avg Trust: {df['Avg_Trust'].iloc[-1]:.1f}")
    print(f"    Final Gini: {df['Gini'].iloc[-1]:.3f}")
    
    print("\n✅ Pipeline complete!")

if __name__ == "__main__":
    run_pipeline()
