import argparse
import os
import re
import sys

import requests
from bs4 import BeautifulSoup
from modules.init_app import init_app
from modules.utils.file_tools import get_node_path, load_from

# Initialisation du projet (comme dans data_analyse)
PROJECT_STRUCTURE, DICT_APP, DICT_SCRIPT_CONFIG, LOGGER, CONST = init_app(
    __file__
)


def load_config(script_name):
    """
    Charge la configuration JSON associée au script (nom_du_script.json)
    dans le répertoire 'conf' défini dans PROJECT_STRUCTURE.
    """
    try:
        config_dir = get_node_path(PROJECT_STRUCTURE, "conf")
    except KeyError as e:
        LOGGER.error(
            f"Répertoire de configuration 'conf' introuvable dans "
            f"PROJECT_STRUCTURE : {e}"
        )
        sys.exit(1)

    config_filename = os.path.join(config_dir, f"{script_name}.json")
    if not os.path.exists(config_filename):
        LOGGER.error(
            f"Fichier de configuration {config_filename} introuvable."
        )
        sys.exit(1)

    try:
        config = load_from(config_filename)
        LOGGER.info(f"Configuration chargée depuis {config_filename}")
        return config
    except Exception as e:
        LOGGER.error(
            f"Erreur chargement fichier config {config_filename} : {e}"
        )
        sys.exit(1)


def generate_filename_from_url(url):
    """
    Crée un nom de fichier à partir de l'URL :
    - remplace tout caractère non alphanumérique par '_'
    - réduit les multiples '_' à un seul
    - supprime les '_' en début et fin de chaîne
    """
    filename_raw = url.replace("https://", "").replace("http://", "")
    filename_clean = re.sub(r"[^a-zA-Z0-9]", "_", filename_raw)
    filename_single_underscore = re.sub(r"_+", "_", filename_clean)
    filename_trimmed = filename_single_underscore.strip("_")
    return filename_trimmed + ".html"


def save_page_content(output_dir, filename, content):
    """
    Sauvegarde le contenu HTML dans output_dir avec le nom filename.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        LOGGER.info(f"Création du répertoire de sortie : {output_dir}")

    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    # Normaliser le chemin pour affichage log (slashs Linux)
    normalized_path = filepath.replace("\\", "/")

    LOGGER.info(f"Page sauvegardée dans {normalized_path}")
    return filepath


def main(url, filename=None):
    LOGGER.info(f"Démarrage du script d'aspiration pour URL : {url}")

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    config = load_config(script_name)

    output_dir = config.get("output_dir")
    if not output_dir:
        LOGGER.error(
            "Le répertoire de sortie 'output_dir' n'est pas défini dans "
            "le fichier de config."
        )
        sys.exit(1)

    if not filename:
        filename = generate_filename_from_url(url)

    try:
        response = requests.get(url)
        response.raise_for_status()
        LOGGER.info(f"Chargement de la page réussi : {url}")

        parser_name = config.get("parser", "html.parser")
        from_encoding = config.get("from_encoding", None)

        if from_encoding:
            soup = BeautifulSoup(
                response.content, parser_name, from_encoding=from_encoding
            )
        else:
            soup = BeautifulSoup(response.content, parser_name)

        save_page_content(output_dir, filename, soup.prettify())

    except requests.RequestException as e:
        LOGGER.error(f"Erreur lors du téléchargement de la page : {e}")
        sys.exit(1)

    LOGGER.info("Fin du script.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script d'aspiration web simple avec BeautifulSoup"
    )
    parser.add_argument(
        "--url", required=True, type=str, help="URL du site à aspirer"
    )
    parser.add_argument(
        "--filename",
        required=False,
        type=str,
        help="Nom du fichier de sortie (optionnel)",
    )
    args = parser.parse_args()

    main(args.url, args.filename)
