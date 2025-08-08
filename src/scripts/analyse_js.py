import json
import os
import re
from typing import Any


def load_json_from_js(filepath: str) -> Any:
    """
    Tente de charger un objet JSON à partir d'un fichier .js ou texte contenant
    éventuellement du JSON.
    Si le fichier ne contient pas du JSON pur, tente d'extraire la première
    portion apparentée via regex.
    """
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Essayer de parser tout le contenu comme du JSON pur
    try:
        data = json.loads(content)
        print("JSON parse success, keys:")
        print(list(data.keys()))
        return data
    except json.JSONDecodeError:
        print("JSON decoding failed, essayer extraction par substring...")

    # Extraire via regex une portion JSON entre accolades { ... }
    match = re.search(r"({.*})", content, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            print("JSON extracted via regex, keys:")
            print(list(data.keys()))
            return data
        except json.JSONDecodeError:
            print("Echec d'extraction JSON via regex.")
            return None
    else:
        print("Aucune portion JSON détectée.")
        return None


def main() -> None:
    # adapte le chemin à ton contexte
    file_path = "D:/Dev/nba/data/reports/script_7.js"
    if not os.path.isfile(file_path):
        print(f"Fichier introuvable : {file_path}")
        return
    _ = load_json_from_js(file_path)


if __name__ == "__main__":
    main()
