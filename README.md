# ices-v2
"Islamic Civilizational Economic Simulator v2 - A calibrated agent-based laboratory for institutional resilience research"

# ICES v2 - Islamic Civilizational Economic Simulator

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![License: CC0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)

## 🏛️ Overview

ICES v2 is a **calibrated agent-based computational laboratory** for studying how institutional portfolios shape long-run resilience, collapse, and attractor formation across civilizations.

**Key Features:**
- **4-layer architecture**: Agent Physics → Economic Mechanisms → Institutions → Metrics
- **Hierarchical Bayesian calibration**: Partial pooling across civilization families
- **Out-of-sample prediction**: Train on 70%, predict 15%, test on 15%
- **Global sensitivity analysis**: Sobol indices to identify driving parameters
- **Falsifiability**: Explicit criteria with minimum variance explained thresholds

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/ices-v2.git
cd ices-v2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run full pipeline
python scripts/run_paper1_pipeline.py

# Launch dashboard
streamlit run src/visualization/dashboard.py
📄 Paper
The paper describing ICES v2 is available as a preprint:

Daghar, M. G. (2026). Institutional Portfolios and Civilizational Resilience: A Calibrated Agent-Based Study of Pre-Modern Economic Systems. arXiv:2606.XXXXX.

📚 Documentation
Architecture

Calibration

Validation

Falsifiability

🤝 Contributing
Contributions are welcome! See CONTRIBUTING.md for guidelines.

📜 License
Code: CC0 1.0 Universal

Research outputs: CC BY-SA 4.0

Data: CC BY-SA 4.0

📖 Citation
bibtex
@software{daghar2026ices,
  author = {Daghar, Marc Gilbert},
  title = {ICES v2: Islamic Civilizational Economic Simulator},
  year = {2026},
  publisher = {Zenodo},
  version = {2.0.0},
  doi = {10.5281/zenodo.XXXXXXX},
  url = {https://github.com/yourusername/ices-v2}
}
