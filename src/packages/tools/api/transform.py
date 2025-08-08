from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class TransformerInterface(ABC):
    @abstractmethod
    def transform(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        pass


class DataTransformer(TransformerInterface):
    def __init__(
        self,
        fields: list[str],
        mapping: dict[str, str] | None = None,
        filter_func: Callable[[dict[str, Any]], bool] | None = None,
    ):
        self._fields = fields
        self._mapping = mapping or {}
        self._filter_func = filter_func

    def transform(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result = []
        for entry in data:
            if self._filter_func and not self._filter_func(entry):
                continue
            new_entry = {}
            for out_field in self._fields:
                in_field = self._mapping.get(out_field, out_field)
                new_entry[out_field] = entry.get(in_field)
            result.append(new_entry)
        return result
