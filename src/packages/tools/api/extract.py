from abc import ABC, abstractmethod

import requests


class ExtractorInterface(ABC):
    @abstractmethod
    def extract(self, endpoint: str, params: dict | None = None) -> dict:
        pass


class ApiExtractor(ExtractorInterface):
    def __init__(self, base_url: str, api_key: str | None = None):
        self._base_url = base_url.rstrip("/")
        self._headers = {}
        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"

    def extract(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{self._base_url}{endpoint}"
        resp = requests.get(
            url, headers=self._headers, params=params, timeout=10
        )
        resp.raise_for_status()
        return resp.json()
