import argparse
import json
from urllib.parse import urlparse

from packages.init_app import init_app
from packages.tools.file import PathUtils
from packages.tools.web.converter import HtmlConverter
from packages.tools.web.crawler import Crawler
from packages.tools.web.extractor import Extractor
from playwright.sync_api import sync_playwright

(
    PROJECT_STRUCTURE,
    DICT_APP,
    DICT_SCRIPT_CONFIG,
    LOGGER,
    CONST,
) = init_app(__file__)


def analyze_site(start_url, max_pages=50, max_depth=3):
    report = {
        "start_url": start_url,
        "robots_txt_present": False,
        "robots_txt_rules": None,
        "found_pages": 0,
        "unique_links": set(),
        "max_depth": 0,
        "domain": urlparse(start_url).netloc,
        "extracted_texts": [],
    }

    crawler = Crawler()
    rp = crawler.get_robots_parser(start_url)
    report["robots_txt_present"] = bool(rp.entries)

    extractor = Extractor()
    HtmlConverter()  # Instanciation si utile ailleurs

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        visited = set()
        queue = [(start_url, 0)]

        while queue and report["found_pages"] < max_pages:
            url, depth = queue.pop(0)

            if url in visited or depth > max_depth:
                continue

            if not crawler.can_fetch(rp, url):
                LOGGER.info(f"Robots.txt bloque l'URL : {url}")
                continue

            # Navigation et récupération du contenu HTML
            page.goto(url)
            html = page.content()

            # Extraction JSON dynamique
            json_objs = extractor.extract_json_objects_from_scripts(html)
            extracted_texts = extractor.extract_texts_from_json_objects(
                json_objs,
                keys_to_extract=["title", "content", "text", "description"],
            )
            report["extracted_texts"].extend(extracted_texts)

            links = extractor.extract_internal_links(html, start_url)

            report["unique_links"].update(links)
            report["found_pages"] += 1
            if depth > report["max_depth"]:
                report["max_depth"] = depth

            visited.add(url)
            for link in links:
                if link not in visited:
                    queue.append((link, depth + 1))

        browser.close()

    report["unique_links"] = list(report["unique_links"])
    return report


def main():
    parser = argparse.ArgumentParser(description="Découverte d'un site web")
    parser.add_argument(
        "--url", required=True, type=str, help="URL racine site"
    )
    args = parser.parse_args()

    report = analyze_site(args.url)

    print(f"--- Rapport de découverte pour {args.url} ---")
    print(f"Robots.txt présent: {report['robots_txt_present']}")
    if report["robots_txt_present"]:
        print("Accès Robots.txt vérifiés")
    print(f"Pages visitées (max 50): {report['found_pages']}")
    print(f"Profondeur max atteinte: {report['max_depth']}")
    print(f"Liens uniques trouvés: {len(report['unique_links'])}")
    print(
        f"Extraits de textes JSON dynamiques : "
        f"{len(report['extracted_texts'])} items"
    )

    output_dir = PathUtils.get_node_path(PROJECT_STRUCTURE, "conf")
    report_path = f"{output_dir}/site_report.json"

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    LOGGER.info(f"Rapport sauvegardé dans {report_path}")


if __name__ == "__main__":
    main()
