# Projet nba

## Description

Ce projet est une structure standard pour un projet Data Science / Machine Learning en Python.

## Arborescence du projet

- `data/`
  - `raw/` : Donn�es brutes import�es, non modifi�es.
  - `processed/` : Donn�es nettoy�es et transform�es, pr�tes � l'analyse.
- `src/modules/` : Package principal contenant le code source Python.
  - `utils/` : Fonctions utilitaires g�n�riques (chargement de donn�es, etc.).
  - `models/` : Mod�les et scripts d'entra�nement.
  - `preprocessing/` : Nettoyage et pr�paration des donn�es.
  - `features/` : Cr�ation et transformation des features.
  - `reporting/` : G�n�ration et gestion des rapports.
- `src/scripts/` : Scripts autonomes pour automatisation.
- `notebooks/` : Carnets Jupyter pour exploration et prototypage.
- `tests/` : Tests unitaires et d'int�gration.
- `logs/` : Fichiers logs.
- `docs/` : Documentation.
  - `reports/html/` : Rapports HTML.
- `.github/workflows/` : Workflows CI/CD.

## Installation
D�pendances disponibles dans `requirements.txt`.

## Utilisation
Exemples d'import :

```
from modules.utils.data_utils import load_data
from modules.preprocessing.data_preprocessing import clean_data
from modules.features.feature_engineering import create_features
from modules.models.train_model import train
from modules.reporting.reporting_utils import generate_report
```
