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

    def get_metadata(
        self,
        fields: list[str] | None = None,
        forms: list[str] | None = None,
        format: str = "csv",
    ) -> pd.DataFrame:
        assert format == "csv"
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

    def export_metadata_raw(
        self,
        fields: list[str] | None = None,
        forms: list[str] | None = None,
        format: str = "csv",
    ) -> str:
        metadata = self.get_metadata(fields=fields, forms=forms, format="csv")
        if format == "json":
            return metadata.to_json(orient="records")
        return metadata.to_csv(index=False)


class SyncMetadataClient(MetadataClient):
    def __init__(self, url: str, token: str, metadata: list[dict[str, str]]) -> None:
        super().__init__(url, token)
        self._metadata = metadata


class FailingClient(FakeClient):
    def get_version(self) -> str:
        raise RuntimeError("bad token")
