import json
import os
import re

from bs4 import BeautifulSoup
from bs4.element import Tag
from playwright.sync_api import sync_playwright


def extract_json_from_scripts(
    html_content: str, json_key_patterns: list[str] | None = None
) -> list[dict]:
    """
    Extrait tous les objets JSON présents dans les balises <script> selon une
    liste de patterns regex.
    """
    if json_key_patterns is None:
        json_key_patterns = [
            r"window\.__INITIAL_DATA__\s*=\s*({.*?});",
            r"window\.__DATA__\s*=\s*({.*?});",
            r"var\s+initialState\s*=\s*({.*?});",
        ]
    soup = BeautifulSoup(html_content, "html.parser")
    scripts = soup.find_all("script")
    extracted_jsons: list[dict] = []
    for i, script in enumerate(scripts):
        if isinstance(script, Tag) and script.string:
            content = script.string
            for pattern in json_key_patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    try:
                        data = json.loads(json_str)
                        extracted_jsons.append(data)
                        print(
                            f"[+] JSON object extracted from script[{i}] "
                            f"with pattern {pattern}"
                        )
                    except json.JSONDecodeError:
                        print(
                            f"[!] JSON decode error in script[{i}] "
                            f"for pattern {pattern}"
                        )
    return extracted_jsons


def save_text_to_file(text: str, filepath: str) -> None:
    """Écrire un texte dans un fichier, en créant les dossiers
    parents si besoin."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)


def main() -> None:
    url = "https://docs.astral.sh/uv"  # À adapter selon tes besoins
    output_dir = "D:/Dev/nba/data/reports/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"Loading page {url} ...")
        page.goto(url, wait_until="networkidle")
        html = page.content()

        os.makedirs(output_dir, exist_ok=True)
        html_path = os.path.join(output_dir, "page_uv.html")
        save_text_to_file(html, html_path)
        print(f"HTML saved to {html_path}")

        # Extraction JSON depuis scripts
        json_objects = extract_json_from_scripts(html)
        print(f"Extracted {len(json_objects)} JSON objects")

        # (Optionnel : tu peux enregistrer chaque objet JSON avec
        # le code ci-dessous)
        for idx, obj in enumerate(json_objects):
            out_path = os.path.join(output_dir, f"script_json_{idx + 1}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(obj, f, indent=2, ensure_ascii=False)
            print(f"Wrote {out_path}")

        browser.close()


if __name__ == "__main__":
    main()
