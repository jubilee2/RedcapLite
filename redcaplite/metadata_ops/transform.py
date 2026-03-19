from __future__ import annotations


def generate_field_label(field_name: str) -> str:
    label = field_name.replace("_", " ")
    if not label:
        return label
    return label[0].upper() + label[1:]
