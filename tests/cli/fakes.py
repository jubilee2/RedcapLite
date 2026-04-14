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
        self.imported_dags: list[dict[str, str]] | None = None
        self.exported_metadata_output_file: str | None = None
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
        self._dags = []

    def get_metadata(
        self,
        fields: list[str] | None = None,
        forms: list[str] | None = None,
        format: str = "csv",
        output_file: str | None = None,
    ) -> pd.DataFrame:
        assert format == "csv"
        self.exported_metadata_output_file = output_file
        metadata = pd.DataFrame(self._metadata)
        if metadata.empty:
            metadata = pd.DataFrame(columns=["field_name", "form_name", "field_type", "field_label"])
        if forms:
            metadata = metadata.loc[metadata["form_name"].isin(forms)]
        if fields:
            metadata = metadata.loc[metadata["field_name"].isin(fields)]
        return metadata

    def import_metadata(self, data: pd.DataFrame, format: str = "csv") -> str:
        self.imported_metadata = data
        self.imported_format = format
        return "1"

    def get_dags(self) -> list[dict[str, str]]:
        return self._dags

    def import_dags(self, data: list[dict[str, str]]) -> str:
        self.imported_dags = data
        return "1"


class SyncMetadataClient(MetadataClient):
    def __init__(
        self,
        url: str,
        token: str,
        metadata: list[dict[str, str]],
        dags: list[dict[str, str]] | None = None,
    ) -> None:
        super().__init__(url, token)
        self._metadata = metadata
        self._dags = dags or []


class FailingClient(FakeClient):
    def get_version(self) -> str:
        raise RuntimeError("bad token")
