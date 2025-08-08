import json
import os

from playwright.sync_api import sync_playwright


def save_json(data: dict, output_dir: str, filename: str) -> None:
    """
    Sauvegarde un objet JSON sous forme de fichier dans output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    full_path = os.path.join(output_dir, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved JSON to {full_path}")


def analyse_xhr(url: str, output_dir: str) -> None:
    """
    Charge une page avec Playwright, intercepte les réponses XHR/fetch,
    et sauvegarde chaque payload JSON de manière unique.
    """
    from urllib.parse import urlparse

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        intercepted_urls: set[str] = set()

        def handle_response(response):
            try:
                if response.request.resource_type in ("xhr", "fetch"):
                    target_url = response.url
                    if target_url in intercepted_urls:
                        return
                    intercepted_urls.add(target_url)
                    # On tente de charger le JSON
                    try:
                        data = response.json()
                    except Exception:
                        return
                    # Génère un nom propre :
                    parsed = urlparse(target_url)
                    fname = (
                        os.path.basename(parsed.path).split("?")[0] or "data"
                    )
                    fname += ".json"
                    save_json(data, output_dir, fname)
            except Exception:
                pass

        page.on("response", handle_response)
        print(f"Loading {url} ...")
        page.goto(url, wait_until="networkidle")
        # Attends pour laisser le temps aux XHR de charger (ajuste au besoin)
        page.wait_for_timeout(5000)
        print(f"Intercepted {len(intercepted_urls)} XHR/Fetch responses")
        browser.close()


if __name__ == "__main__":
    url = "https://docs.astral.sh/uv"  # Remplace par ton URL cible
    output_dir = "D:/Dev/nba/data/reports/"
    analyse_xhr(url, output_dir)
