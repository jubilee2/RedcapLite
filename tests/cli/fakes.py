from __future__ import annotations

import pandas as pd


class FakeClient:
    def __init__(self, url: str, token: str) -> None:
        self.url = url
        self.token = token

    def get_version(self) -> str:
        return "14.0.0"


class MetadataClient(FakeClient):
    def __init__(self, url: str, token: str) -> None:
        super().__init__(url, token)
        self.imported_metadata: pd.DataFrame | None = None
        self.imported_format: str | None = None
        self._metadata = [
            {
                "field_name": "record_id",
                "form_name": "enrollment",
                "field_type": "text",
                "field_label": "Record ID",
                "required_field": "y",
            },
            {
                "field_name": "age",
                "form_name": "demographics",
                "field_type": "text",
                "field_label": "Age",
                "required_field": "",
            },
        ]

    def get_metadata(self, format: str = "csv") -> pd.DataFrame:
        assert format == "csv"
        return pd.DataFrame(self._metadata)

    def import_metadata(self, data: pd.DataFrame, format: str = "csv") -> str:
        self.imported_metadata = data
        self.imported_format = format
        return "1"


class FailingClient(FakeClient):
    def get_version(self) -> str:
        raise RuntimeError("bad token")
