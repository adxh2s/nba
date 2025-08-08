from typing import Any

import requests
from bs4 import BeautifulSoup


class ApiDiscoverer:
    """
    Discover API endpoints using OpenAPI or HTML scraping.
    """

    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")

    def discover_openapi(self) -> list[dict[str, Any]]:
        """
        Try to discover endpoints from OpenAPI or swagger JSON specs.

        Returns:
            List of endpoint dictionaries with path, method, summary.
        """
        for suffix in ("/openapi.json", "/swagger.json"):
            url = f"{self._base_url}{suffix}"
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                spec = resp.json()
                endpoints = []
                for path, ops in spec.get("paths", {}).items():
                    for method, details in ops.items():
                        endpoints.append(
                            {
                                "path": path,
                                "method": method.lower(),
                                "summary": details.get("summary", ""),
                            }
                        )
                return endpoints
            except Exception:
                continue
        return []

    def discover_html_docs(
        self, doc_url: str | None = None
    ) -> list[dict[str, str]]:
        """
        Parse HTML documentation page for endpoints.

        Args:
            doc_url: URL to documentation page. Defaults to base_url + "/docs".

        Returns:
            List of endpoints dictionaries.
        """
        url = doc_url or f"{self._base_url}/docs"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            endpoints = []
            codes = soup.find_all("code")
            for code in codes:
                text = code.get_text(strip=True)
                if text.startswith("/"):
                    summary = ""
                    parent = code.parent
                    next_p = parent.find_next_sibling("p") if parent else None
                    if next_p:
                        summary = next_p.get_text(strip=True)
                    endpoints.append(
                        {"path": text, "method": "get", "summary": summary}
                    )
            return endpoints
        except Exception:
            return []

    def discover_brute(self, candidates: list[str]) -> list[str]:
        """
        Test candidate endpoints by sending GET requests.

        Args:
            candidates: List of relative endpoints.

        Returns:
            List of endpoints responding with 200, 401 or 403.
        """
        found = []
        for endpoint in candidates:
            url = f"{self._base_url}{endpoint}"
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code in {200, 401, 403}:
                    found.append(endpoint)
            except Exception:
                continue
        return found
