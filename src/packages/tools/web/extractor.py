from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag


class Extractor:
    """Utilities for extracting links and JSON from HTML content."""

    def extract_internal_links(
        self, html_content: str, base_url: str
    ) -> set[str]:
        """Extract internal links within the same base_url domain."""
        soup = BeautifulSoup(html_content, "html.parser")
        links: set[str] = set()
        base_domain = urlparse(base_url).netloc

        for a in soup.find_all("a"):
            if not isinstance(a, Tag):
                continue

            href = a.attrs.get("href")
            if not isinstance(href, str):
                continue

            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            if parsed.netloc == base_domain and full_url.startswith(base_url):
                full_url = full_url.split("#")[0]
                links.add(full_url)
        return links

    def extract_json_objects_from_scripts(
        self,
        html_content: str,
        json_key_patterns: list[str] | None = None,
    ) -> list[dict]:
        """
        Extract JSON objects embedded in script tags matching key patterns.
        """
        import json
        import re

        if json_key_patterns is None:
            json_key_patterns = [
                r"window\.__INITIAL_DATA__\s*=\s*({.*?});",
                r"window\.__DATA__\s*=\s*({.*?});",
                r"var\s+initialState\s*=\s*({.*?});",
            ]

        soup = BeautifulSoup(html_content, "html.parser")
        scripts = soup.find_all("script")

        results: list[dict] = []
        for script in scripts:
            if not isinstance(script, Tag):
                continue
            if not script.string:
                continue
            script_content = script.string.strip()
            for pattern in json_key_patterns:
                match = re.search(pattern, script_content, flags=re.DOTALL)
                if match:
                    json_str = match.group(1)
                    try:
                        data = json.loads(json_str)
                        results.append(data)
                    except json.JSONDecodeError:
                        continue
        return results

    def extract_texts_from_json_objects(
        self,
        json_objs: list[dict],
        keys_to_extract: list[str] | None = None,
    ) -> list[str]:
        """Extract texts from JSON objects given keys to extract."""
        if keys_to_extract is None:
            keys_to_extract = ["title", "content", "text", "description"]

        texts: list[str] = []

        def recursive_extract(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k in keys_to_extract and isinstance(v, str):
                        texts.append(v)
                    else:
                        recursive_extract(v)
            elif isinstance(obj, list):
                for item in obj:
                    recursive_extract(item)

        for obj in json_objs:
            recursive_extract(obj)

        return texts
