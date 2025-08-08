from pathlib import Path

from packages.tools.file.io_utils import FileTools

from .export import CsvExporter
from .extract import ApiExtractor
from .transform import DataTransformer


class LoadDataFromApi:
    def __init__(self, config_path: str, file_tools: FileTools):
        self._file_tools = file_tools
        self._config = self._file_tools.load_from(config_path)
        api_conf = self._config.get("api", {})
        self._base_url = api_conf.get("base_url", "")
        self._api_key = api_conf.get("api_key", None)
        self._exports = api_conf.get("exports", [])
        self._version = self._config.get("version", "v1")
        self._date_mask = self._config.get("date_mask", "%Y%m%d")
        self._output_dir = Path(self._config.get("output_dir", "data/raw"))

        self._extractor = ApiExtractor(self._base_url, self._api_key)
        self._exporter = CsvExporter(str(self._output_dir), self._date_mask)

    def run(self) -> None:
        for export_conf in self._exports:
            endpoint = export_conf.get("endpoint", "")
            filename = export_conf.get("filename", "")
            fields = export_conf.get("fields", [])
            mapping = export_conf.get("mapping", {})
            params = export_conf.get("params", None)
            filter_func = None

            print(f"Extracting from {endpoint}...")
            raw_data = self._extractor.extract(endpoint, params=params)

            if isinstance(raw_data, dict):
                data_list = (
                    raw_data.get("data")
                    or raw_data.get("results")
                    or raw_data.get(filename)
                    or raw_data
                )
            else:
                data_list = raw_data

            if not isinstance(data_list, list):
                data_list = [data_list]

            transformer = DataTransformer(fields, mapping, filter_func)
            rows = transformer.transform(data_list)

            self._exporter.export(rows, filename, self._version)
