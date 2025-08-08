import argparse
import sys

from packages.init_app import init_app
from packages.tools.file import FileTools, PathUtils
from packages.tools.web.crawler import Crawler
from packages.tools.web.extractor import Extractor
from packages.tools.web.resources import ResourceManager
from packages.tools.web.utils import WebUtils
from playwright.sync_api import sync_playwright

(
    PROJECT_STRUCTURE,
    DICT_APP,
    DICT_SCRIPT_CONFIG,
    LOGGER,
    CONST,
) = init_app(__file__)


def get_output_dir(config: dict) -> str:
    """
    Retrieve or determine output directory from config and PROJECT_STRUCTURE.

    Args:
        config (dict): Script configuration.

    Returns:
        str: Output directory path.
    """
    try:
        default_output_dir = PathUtils.get_node_path(
            PROJECT_STRUCTURE, "docs", "reports", "html"
        )
        if not isinstance(default_output_dir, str):
            raise TypeError(
                "Le chemin docs/reports/html doit être une chaîne."
            )
    except KeyError:
        LOGGER.error(
            "Chemin docs/reports/html manquant dans PROJECT_STRUCTURE"
        )
        default_output_dir = ""

    output_dir = config.get("output_dir", default_output_dir)
    if not isinstance(output_dir, str) or not output_dir:
        LOGGER.error(
            "output_dir non défini dans config "
            "et aucun chemin par défaut trouvé"
        )
        sys.exit(1)
    return output_dir


def scrape_site(
    start_url: str,
    output_dir: str,
    max_pages: int = 100,
    max_depth: int = 3,
    user_agent: str = "*",
    min_delay: float = 1,
    max_delay: float = 3,
    parser: str = "lxml",
    from_encoding: str = "utf-8",
    preserve_whitespace_tags: list[str] | None = None,
) -> None:
    """
    Recursively scrape a site, respecting robots.txt,
    limiting volume and depth, pausing between requests,
    and saving pages/resources.
    """
    if preserve_whitespace_tags is None:
        preserve_whitespace_tags = ["pre", "textarea"]

    crawler = Crawler()
    extractor = Extractor()
    resource_manager = ResourceManager()

    rp = crawler.get_robots_parser(start_url)
    visited: set[str] = set()
    queue: list[tuple[str, int]] = [(start_url, 0)]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        while queue and len(visited) < max_pages:
            url, depth = queue.pop(0)
            if url in visited or depth > max_depth:
                continue

            if not crawler.can_fetch(rp, url, user_agent):
                LOGGER.info(f"Bloqué par robots.txt : {url}")
                continue

            filename_embedded = (
                WebUtils.generate_filename_from_url(url) + "_embedded.html"
            )
            filename_text = (
                WebUtils.generate_filename_from_url(url) + "_text.txt"
            )

            if WebUtils.is_cached(
                output_dir, filename_embedded
            ) and WebUtils.is_cached(output_dir, filename_text):
                LOGGER.info(f"Cache trouvé, saute {url}")
                visited.add(url)
                continue

            LOGGER.info(f"Aspiration {url} à profondeur {depth}")
            html_content = WebUtils.fetch_page_with_playwright(page, url)

            resource_manager.extract_and_download_resources(
                page, url, output_dir
            )
            WebUtils.save_content(output_dir, filename_embedded, html_content)

            json_objs = extractor.extract_json_objects_from_scripts(
                html_content
            )
            extracted_texts = extractor.extract_texts_from_json_objects(
                json_objs,
                keys_to_extract=["title", "content", "text", "description"],
            )

            json_text_concat = "\n\n".join(extracted_texts)

            text_content = WebUtils.html_to_text(
                html_content,
                parser=parser,
                from_encoding=from_encoding,
                preserve_whitespace_tags=preserve_whitespace_tags,
            )
            full_text_content = f"{text_content}\n\n{json_text_concat}".strip()

            WebUtils.save_content(output_dir, filename_text, full_text_content)

            visited.add(url)

            new_links = extractor.extract_internal_links(
                html_content, start_url
            )
            new_to_add = new_links - visited
            for link in new_to_add:
                queue.append((link, depth + 1))

            WebUtils.delay_between_requests(min_delay, max_delay)

        browser.close()


def main():
    parser = argparse.ArgumentParser(description="Script d'aspiration avancé")
    parser.add_argument("--url", required=True, type=str, help="URL racine")
    parser.add_argument(
        "--config_path",
        required=True,
        type=str,
        help="Chemin vers fichier JSON config (découverte)",
    )
    args = parser.parse_args()

    config = FileTools.load_from(args.config_path)
    output_dir = get_output_dir(config)

    max_pages = config.get("max_pages", 100)
    max_depth = config.get("max_depth", 3)
    min_delay = config.get("min_delay", 1)
    max_delay = config.get("max_delay", 3)
    parser_name = config.get("parser", "lxml")
    encoding = config.get("from_encoding", "utf-8")
    preserve_tags = config.get("preserve_whitespace_tags", ["pre", "textarea"])

    try:
        scrape_site(
            args.url,
            output_dir,
            max_pages=max_pages,
            max_depth=max_depth,
            min_delay=min_delay,
            max_delay=max_delay,
            parser=parser_name,
            from_encoding=encoding,
            preserve_whitespace_tags=preserve_tags,
        )
    except Exception as err:
        LOGGER.error(f"Erreur durant le scraping : {err}")
        sys.exit(1)

    LOGGER.info("Fin du script.")


if __name__ == "__main__":
    main()
