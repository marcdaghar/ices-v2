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

## 📄 Paper

The paper describing ICES v2 is available as a preprint:

> Daghar, M. G. (2026). **Institutional Portfolios and Civilizational Resilience: Hierarchical Bayesian Evidence from 10 Pre-Modern Economies**. *arXiv:2606.XXXXX*.

📄 **Read the full manuscript**: [paper/manuscript.pdf](paper/manuscript.pdf)

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/marcdaghar/ices-v2.git
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
@software{daghar2026ices,
  author = {Daghar, Marc Gilbert},
  title = {ICES v2: Islamic Civilizational Economic Simulator},
  year = {2026},
  publisher = {Zenodo},
  version = {2.0.0},
  doi = {10.5281/zenodo.XXXXXXX},
  url = {https://github.com/marcdaghar/ices-v2}
}
📁 Project Structure

ices-v2/
├── paper/
│   ├── manuscript.pdf          # 📄 Full paper (LaTeX compiled)
│   └── manuscript.tex          # 📝 LaTeX source
├── src/                        # Source code
│   ├── agents/                 # Agent classes
│   ├── layers/                 # 4-layer architecture
│   ├── models/                 # Main model
│   ├── analysis/               # Analysis modules
│   └── visualization/          # Dashboard
├── data/                       # Historical data
├── scripts/                    # Execution scripts
├── notebooks/                  # Jupyter notebooks
├── tests/                      # Unit tests
└── results/                    # Simulation outputs

🔬 Reproducibility
All results in the paper can be reproduced by running:
python scripts/run_paper1_pipeline.py

See docs/replication.md for detailed instructions.


---

## 📁 3. STRUCTURE FINALE
ices-v2/
├── paper/
│ ├── manuscript.tex # 📝 Article LaTeX
│ ├── manuscript.pdf # 📄 Article PDF (à compiler)
│ └── references.bib # 📚 Bibliographie
├── README.md # ✅ Mis à jour avec lien vers l'article
├── src/ # Code source
├── data/ # Données historiques
├── scripts/ # Scripts d'exécution
├── notebooks/ # Jupyter notebooks
├── tests/ # Tests unitaires
├── requirements.txt
├── pyproject.toml
├── LICENSE
├── CONTRIBUTING.md
└── CITATION.cff


---

## 🚀 COMMANDES POUR AJOUTER CES FICHIERS

```bash
# Créer le dossier paper
mkdir -p paper

# Ajouter les fichiers
touch paper/manuscript.tex
touch paper/references.bib
touch paper/.gitkeep

# Compiler le PDF (nécessite LaTeX)
cd paper
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex
cd ..

# Ou utiliser Overleaf pour la compilation en ligne
# Télécharger manuscript.tex et references.bib sur Overleaf

# Vérifier que le README est à jour
cat README.md | grep -A 5 "Paper"
