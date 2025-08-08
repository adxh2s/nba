import csv
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any


class ExporterInterface(ABC):
    @abstractmethod
    def export(
        self, data: list[dict[str, Any]], filename: str, version: str
    ) -> None:
        pass


class CsvExporter(ExporterInterface):
    def __init__(self, output_dir: str, date_mask: str = "%Y%m%d"):
        self._output_dir = Path(output_dir)
        self._date_mask = date_mask

    def export(
        self, data: list[dict[str, Any]], filename: str, version: str
    ) -> None:
        if not data:
            print("No data to export.")
            return

        date_str = datetime.today().strftime(self._date_mask)
        safe_version = version.replace("/", "_").replace(" ", "_")
        filename_full = f"{date_str}_{filename}_{safe_version}.csv"
        self._output_dir.mkdir(parents=True, exist_ok=True)
        filepath = self._output_dir / filename_full

        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"Export succeeded: {filepath.resolve()}")
