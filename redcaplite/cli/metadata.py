from __future__ import annotations

from argparse import Namespace
from typing import Any, Dict, Iterable, List

from redcaplite import RedcapClient
from redcaplite.auth import TokenStore
from redcaplite.cli.output import print_error, print_key_values
from redcaplite.config import ProfileStore


METADATA_SHOW_FIELDS: List[str] = [
    "field_name",
    "form_name",
    "field_type",
    "field_label",
    "select_choices_or_calculations",
    "field_note",
    "text_validation_type_or_show_slider_number",
    "required_field",
    "identifier",
    "branching_logic",
    "section_header",
]


class MetadataService:
    def __init__(self, profile_store: ProfileStore | None = None, token_store: TokenStore | None = None) -> None:
        self.profile_store = profile_store or ProfileStore()
        self.token_store = token_store or TokenStore()

    def list_fields(self, profile_name: str, form_name: str | None = None) -> int:
        client = self._client(profile_name)
        metadata = client.get_metadata(format="json", forms=[form_name] if form_name else [])
        for row in metadata:
            print_key_values(
                row,
                keys=["field_name", "form_name", "field_type", "field_label"],
            )
            print()
        return 0

    def show_field(self, profile_name: str, field_name: str) -> int:
        client = self._client(profile_name)
        metadata = client.get_metadata(format="json", fields=[field_name])
        if not metadata:
            print_error(f'field "{field_name}" not found.')
            return 1
        print_key_values(metadata[0], METADATA_SHOW_FIELDS)
        return 0

    def placeholder(self, action: str) -> int:
        print_error(f'metadata {action} is not available yet.')
        return 1

    def _client(self, profile_name: str) -> RedcapClient:
        profile = self.profile_store.get(profile_name)
        if profile is None:
            raise ValueError(f'profile "{profile_name}" not found')
        token = self.token_store.get(profile_name)
        if token is None:
            raise ValueError(f'access for profile "{profile_name}" not found')
        return RedcapClient(profile.url, token)


def handle_metadata_command(args: Namespace) -> int:
    service = MetadataService()
    try:
        if args.metadata_command == "list-fields":
            return service.list_fields(args.profile, args.form)
        if args.metadata_command == "show-field":
            return service.show_field(args.profile, args.field_name)
        if args.metadata_command == "add-field":
            return service.placeholder("add-field")
        if args.metadata_command == "edit-field":
            return service.placeholder("edit-field")
        if args.metadata_command == "remove-field":
            return service.placeholder("remove-field")
    except ValueError as exc:
        message = str(exc)
        hint = None
        if message.startswith("profile"):
            hint = f"run `rcl access {args.profile}`"
        print_error(message, hint)
        return 1
    return 1
