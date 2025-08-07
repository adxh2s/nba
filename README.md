# Projet nba

## Description

Ce projet est une structure standard pour un projet Data Science / Machine Learning en Python.

## Arborescence du projet

- `data/`
  - `raw/` : Données brutes importées, non modifiées.
  - `processed/` : Données nettoyées et transformées, prêtes à l'analyse.
- `src/modules/` : Package principal contenant le code source Python.
  - `utils/` : Fonctions utilitaires génériques (chargement de données, etc.).
  - `models/` : Modèles et scripts d'entraînement.
  - `preprocessing/` : Nettoyage et préparation des données.
  - `features/` : Création et transformation des features.
  - `reporting/` : Génération et gestion des rapports.
- `src/scripts/` : Scripts autonomes pour automatisation.
- `notebooks/` : Carnets Jupyter pour exploration et prototypage.
- `tests/` : Tests unitaires et d'intégration.
- `logs/` : Fichiers logs.
- `docs/` : Documentation.
  - `reports/html/` : Rapports HTML.
- `.github/workflows/` : Workflows CI/CD.

## Installation
Dépendances disponibles dans `requirements.txt`.

## Utilisation
Exemples d'import :

```
from modules.utils.data_utils import load_data
from modules.preprocessing.data_preprocessing import clean_data
from modules.features.feature_engineering import create_features
from modules.models.train_model import train
from modules.reporting.reporting_utils import generate_report
```
