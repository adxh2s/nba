import argparse
import os

import yaml


def load_structure_config(config_path):
    """
    Charge la configuration de l'arborescence depuis un fichier YAML.
    """
    with open(config_path) as file:
        return yaml.safe_load(file)


def create_project_structure(root_dir, structure):
    """
    Crée les dossiers et sous-dossiers selon la configuration chargée.
    """
    for folder, subfolders in structure.items():
        folder_path = os.path.join(root_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        for sub in subfolders:
            os.makedirs(os.path.join(folder_path, sub), exist_ok=True)


def create_init_files(root_dir, structure):
    """
    Crée les fichiers __init__.py dans tous les sous-dossiers de /src/modules/
    indiqués dans la structure YAML, et dans tests si présent.
    """
    src_path = os.path.join(root_dir, "src")
    modules = structure.get("src", {}).get("modules", [])
    modules_path = os.path.join(src_path, "modules")
    os.makedirs(modules_path, exist_ok=True)

    # Créer __init__.py dans src/modules
    with open(os.path.join(modules_path, "__init__.py"), "w") as f:
        f.write("# Package modules\n")

    # Créer __init__.py dans chaque sous-module
    for sub in modules:
        sub_path = os.path.join(modules_path, sub)
        os.makedirs(sub_path, exist_ok=True)
        with open(os.path.join(sub_path, "__init__.py"), "w") as f:
            f.write(f"# Package modules.{sub}\n")

    # Option : créer aussi dans tests (pour compatibilité)
    tests_path = os.path.join(root_dir, "tests")
    if os.path.exists(tests_path):
        with open(os.path.join(tests_path, "__init__.py"), "w") as f:
            f.write("# Package tests\n")


def create_initial_modules(root_dir, structure):
    """
    Crée les modules Python initiaux dans leurs dossiers respectifs
    sous src/modules/ avec du code d'exemple conforme.
    """
    # Exemple de mapping des modules avec chemins adaptés
    # à la nouvelle structure
    modules_code = {
        "src/modules/preprocessing/data_preprocessing.py": (
            "# Module de traitement et nettoyage des données\n\n"
            "def clean_data(data):\n"
            '    """Fonction pour nettoyer les données"""\n'
            "    pass\n"
        ),
        "src/modules/features/feature_engineering.py": (
            "# Module pour l'extraction et la transformation "
            "des caractéristiques\n\n"
            "def create_features(data):\n"
            '    """Fonction pour créer des features"""\n'
            "    pass\n"
        ),
        "src/modules/utils/data_utils.py": (
            "# Fonctions utilitaires pour la gestion des données\n\n"
            "def load_data(path):\n"
            '    """Charger les données depuis un chemin donné"""\n'
            "    pass\n"
        ),
        "src/modules/models/train_model.py": (
            "# Script d'entraînement du modèle\n\n"
            "def train():\n"
            '    """Fonction d\'entraînement du modèle"""\n'
            "    pass\n\n"
            "if __name__ == '__main__':\n"
            "    train()\n"
        ),
        "src/modules/reporting/reporting_utils.py": (
            "# Module pour génération et gestion des rapports\n\n"
            "def generate_report(data, output_path):\n"
            '    """Génère un rapport à partir des données et '
            'sauvegarde vers output_path"""\n'
            "    pass\n"
        ),
    }

    for relative_path, content in modules_code.items():
        path = os.path.join(root_dir, *relative_path.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)


def create_readme(root_dir):
    """
    Crée un README.md documentant l'organisation du projet et ses dossiers.
    """
    readme_path = os.path.join(root_dir, "README.md")
    with open(readme_path, "w") as f:
        f.write(
            f"# Projet {os.path.basename(root_dir)}\n\n"
            "## Description\n\n"
            "Ce projet est une structure standard pour un projet "
            "Data Science / Machine Learning en Python.\n\n"
            "## Arborescence du projet\n\n"
            "- `data/`\n"
            "  - `raw/` : Données brutes importées, non modifiées.\n"
            "  - `processed/` : Données nettoyées et transformées, "
            "prêtes à l'analyse.\n"
            "- `src/modules/` : Package principal contenant le code source "
            "Python.\n"
            "  - `utils/` : Fonctions utilitaires génériques (chargement de "
            "données, etc.).\n"
            "  - `models/` : Modèles et scripts d'entraînement.\n"
            "  - `preprocessing/` : Nettoyage et préparation des données.\n"
            "  - `features/` : Création et transformation des features.\n"
            "  - `reporting/` : Génération et gestion des rapports.\n"
            "- `src/scripts/` : Scripts autonomes pour automatisation.\n"
            "- `notebooks/` : Carnets Jupyter pour exploration "
            "et prototypage.\n"
            "- `tests/` : Tests unitaires et d'intégration.\n"
            "- `logs/` : Fichiers logs.\n"
            "- `docs/` : Documentation.\n"
            "  - `reports/html/` : Rapports HTML.\n"
            "- `.github/workflows/` : Workflows CI/CD.\n\n"
            "## Installation\n"
            "Dépendances disponibles dans `requirements.txt`.\n\n"
            "## Utilisation\n"
            "Exemples d'import :\n\n"
            "```\n"
            "from modules.utils.data_utils import load_data\n"
            "from modules.preprocessing.data_preprocessing import clean_data\n"
            "from modules.features.feature_engineering import create_features"
            "\n"
            "from modules.models.train_model import train\n"
            "from modules.reporting.reporting_utils import generate_report\n"
            "```\n"
        )


def create_requirements(root_dir):
    """
    Crée un fichier requirements.txt complet et commenté.
    """
    requirements = """
# Bibliothèque pour la gestion YAML (configuration projet)
PyYAML>=6.0

# Bibliothèques principales Data Science et Machine Learning

# Manipulation des données
pandas>=1.5.0

# Calcul numérique
numpy>=1.23.0

# Machine Learning
scikit-learn>=1.2.0

# Visualisation
matplotlib>=3.7.0
seaborn>=0.12.0

# Traitement parallèle et big data
dask[dataframe]>=2023.3.0

# Compatibilité Python >= 3.10 (par exemple 3.11 par défaut)
# Ajuster en fonction de vos besoins spécifiques pour chaque package.
# Exemple d'utilisation d'expressions conditionnelles pip :
# packageX>=1.0 ; python_version >= "3.11"
# futures>=3.1.1 ; python_version < "3.11"
# typing_extensions>=4.5.0 ; python_version < "3.10"
"""
    with open(os.path.join(root_dir, "requirements.txt"), "w") as f:
        f.write(requirements.strip() + "\n")


def create_pyproject(root_dir):
    """
    Crée un fichier pyproject.toml simple et minimaliste.
    """
    pyproject_content = f"""
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "{os.path.basename(root_dir)}"
version = "0.1.0"
description = "Un projet Data ML en Python"
authors = [{{ name = "Auteur", email = "auteur@example.com" }}]
readme = "README.md"
requires-python = ">=3.10"

[tool.black]
line-length = 88
"""
    with open(os.path.join(root_dir, "pyproject.toml"), "w") as f:
        f.write(pyproject_content.strip())


def main():
    parser = argparse.ArgumentParser(
        description="Créer arborescence projet Data ML Python "
        "basée sur config YAML"
    )
    parser.add_argument(
        "root_dir",
        nargs="?",
        default=None,
        help="Chemin du dossier racine du projet (optionnel)",
    )
    parser.add_argument(
        "--config",
        default="conf/project_structure.yaml",
        help="Chemin fichier YAML de configuration",
    )
    args = parser.parse_args()

    if args.root_dir is None:
        root_dir = os.getcwd()
        print(
            f"Aucun dossier racine spécifié. Utilisation du répertoire"
            f"courant : {root_dir}"
        )
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.join(script_dir, args.root_dir)
        print(
            f"Dossier spécifié : {args.root_dir}. "
            f"Structure créée dans : {root_dir}"
        )

    structure = load_structure_config(args.config)
    create_project_structure(root_dir, structure)
    create_init_files(root_dir, structure)
    create_initial_modules(root_dir, structure)
    create_readme(root_dir)
    create_requirements(root_dir)
    create_pyproject(root_dir)

    print(f"Projet créé avec succès dans le dossier : {root_dir}")


if __name__ == "__main__":
    main()
