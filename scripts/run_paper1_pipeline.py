# scripts/run_paper1_pipeline.py
"""
Complete pipeline for ICES v2 Paper 1.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

from src.models.ices_model import ICESModel, HierarchicalBayesianCalibrator, SobolAnalyzer

def load_historical_data():
    """Load historical data for all civilizations."""
    data_dir = Path("data/historical")
    data = {}
    for csv_file in data_dir.glob("*.csv"):
        civ_name = csv_file.stem
        try:
            data[civ_name] = pd.read_csv(csv_file)
            print(f"  Loaded {civ_name}: {len(data[civ_name])} years")
        except Exception as e:
            print(f"  Warning: Could not load {civ_name}: {e}")
    return data

def run_pipeline():
    print("="*60)
    print("ICES v2 PAPER 1 PIPELINE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Create results directory
    results_dir = Path("results/paper1")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Run simulation
    print("\n[1] Running ICES simulation...")
    model = ICESModel(n_households=60, n_merchants=20, n_farmers=20,
                      use_zakat=True, use_waqf=True, use_crd=True,
                      monetary_system="dinar")
    df = model.run(n_steps=200)
    df.to_csv(results_dir / "simulation_results.csv", index=False)
    print(f"    Simulation completed: {len(df)} steps")
    print(f"    Final CI: {df['Civilization_Index'].iloc[-1]:.3f}")
    print(f"    Final Gini: {df['Gini'].iloc[-1]:.3f}")
    
    # Step 2: Load historical data
    print("\n[2] Loading historical data...")
    hist_data = load_historical_data()
    
    # Step 3: Hierarchical Bayesian Calibration (if data available)
    if hist_data:
        print("\n[3] Running Hierarchical Bayesian Calibration...")
        calibrator = HierarchicalBayesianCalibrator(hist_data)
        trace = calibrator.calibrate(n_samples=1000, tune=500, chains=2)
        # Save trace summary
        trace_summary = {
            "civilizations": list(hist_data.keys()),
            "method": "Hierarchical Bayesian",
            "chains": 2,
            "samples": 1000
        }
        with open(results_dir / "calibration_summary.json", "w") as f:
            json.dump(trace_summary, f, indent=2)
        print("    Calibration completed")
    
    # Step 4: Generate summary
    print("\n[4] Generating summary report...")
    summary = {
        "timestamp": datetime.now().isoformat(),
        "pipeline_status": "COMPLETE",
        "simulation": {
            "steps": len(df),
            "final_ci": float(df['Civilization_Index'].iloc[-1]),
            "final_gini": float(df['Gini'].iloc[-1]),
            "final_trust": float(df['Avg_Trust'].iloc[-1])
        },
        "data": {
            "civilizations_loaded": list(hist_data.keys()) if hist_data else []
        }
    }
    
    with open(results_dir / "summary_report.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Step 5: Generate figures
    print("\n[5] Generating figures...")
    try:
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Civilization Index
        axes[0, 0].plot(df['Civilization_Index'], color='blue')
        axes[0, 0].set_title('Civilization Index')
        axes[0, 0].set_xlabel('Step')
        axes[0, 0].set_ylabel('CI')
        
        # Wealth and Trust
        axes[0, 1].plot(df['Avg_Wealth'], color='green', label='Wealth')
        axes[0, 1].plot(df['Avg_Trust'], color='red', label='Trust')
        axes[0, 1].set_title('Wealth & Trust')
        axes[0, 1].legend()
        
        # Gini
        axes[1, 0].plot(df['Gini'], color='orange')
        axes[1, 0].set_title('Gini Coefficient')
        axes[1, 0].set_xlabel('Step')
        
        # Zakat and Waqf
        if 'Zakat_Treasury' in df.columns:
            axes[1, 1].plot(df['Zakat_Treasury'], color='purple', label='Zakat')
            axes[1, 1].plot(df['Waqf_Endowment'], color='brown', label='Waqf')
            axes[1, 1].set_title('Institutions')
            axes[1, 1].legend()
        
        plt.tight_layout()
        plt.savefig(results_dir / "figures" / "simulation_results.png", dpi=150)
        print("    Figures saved to results/paper1/figures/")
    except Exception as e:
        print(f"    Warning: Could not generate figures: {e}")
    
    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)
    print(f"Results saved to: {results_dir}")
    print("\nKey metrics:")
    print(f"  - Final Civilization Index: {summary['simulation']['final_ci']:.3f}")
    print(f"  - Final Gini: {summary['simulation']['final_gini']:.3f}")
    print(f"  - Final Trust: {summary['simulation']['final_trust']:.1f}")

if __name__ == "__main__":
    run_pipeline()
