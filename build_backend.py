"""Minimal PEP 517 build backend for offline packaging in tests."""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path
import re
import tempfile
from typing import Iterable
import tarfile
from zipfile import ZIP_DEFLATED, ZipFile

import tomllib

ROOT = Path(__file__).resolve().parent
PYPROJECT = ROOT / "pyproject.toml"


def _load_project_metadata() -> dict:
    with PYPROJECT.open("rb") as pyproject_file:
        return tomllib.load(pyproject_file)["project"]


PROJECT = _load_project_metadata()
NAME = PROJECT["name"]
VERSION = PROJECT["version"]


def _normalize_distribution_name(name: str) -> str:
    return re.sub(r"[-_.]+", "_", name)


DIST_INFO = f"{_normalize_distribution_name(NAME)}-{VERSION}.dist-info"


def _iter_package_files() -> Iterable[Path]:
    for path in sorted((ROOT / NAME).rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            yield path


def _metadata_text() -> str:
    lines = [
        "Metadata-Version: 2.1",
        f"Name: {NAME}",
        f"Version: {VERSION}",
        f"Summary: {PROJECT.get('description', '')}",
        f"Requires-Python: {PROJECT.get('requires-python', '')}",
    ]
    for dependency in PROJECT.get("dependencies", []):
        lines.append(f"Requires-Dist: {dependency}")
    return "\n".join(lines) + "\n"


def _wheel_text() -> str:
    return "\n".join([
        "Wheel-Version: 1.0",
        "Generator: redcaplite.build_backend",
        "Root-Is-Purelib: true",
        "Tag: py3-none-any",
        "",
    ])


def _entry_points_text() -> str:
    scripts = PROJECT.get("scripts", {})
    if not scripts:
        return ""
    lines = ["[console_scripts]"]
    lines.extend(f"{name} = {target}" for name, target in scripts.items())
    return "\n".join(lines) + "\n"


def _record_line(path: str, data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    encoded_digest = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return f"{path},sha256={encoded_digest},{len(data)}"


def _build_wheel_file(wheel_path: Path) -> None:
    record_rows: list[str] = []
    with ZipFile(wheel_path, "w", compression=ZIP_DEFLATED) as wheel_file:
        for source_path in _iter_package_files():
            archive_path = source_path.relative_to(ROOT).as_posix()
            data = source_path.read_bytes()
            wheel_file.writestr(archive_path, data)
            record_rows.append(_record_line(archive_path, data))

        dist_info_files = {
            f"{DIST_INFO}/METADATA": _metadata_text().encode("utf-8"),
            f"{DIST_INFO}/WHEEL": _wheel_text().encode("utf-8"),
        }
        entry_points_text = _entry_points_text()
        if entry_points_text:
            dist_info_files[f"{DIST_INFO}/entry_points.txt"] = entry_points_text.encode("utf-8")

        for archive_path, data in dist_info_files.items():
            wheel_file.writestr(archive_path, data)
            record_rows.append(_record_line(archive_path, data))

        record_path = f"{DIST_INFO}/RECORD"
        record_rows.append(f"{record_path},,")
        wheel_file.writestr(record_path, "\n".join(record_rows) + "\n")



def build_wheel(
    wheel_directory: str,
    config_settings: dict | None = None,
    metadata_directory: str | None = None,
) -> str:
    del config_settings, metadata_directory
    wheel_name = f"{_normalize_distribution_name(NAME)}-{VERSION}-py3-none-any.whl"
    wheel_path = Path(wheel_directory) / wheel_name
    _build_wheel_file(wheel_path)
    return wheel_name



def build_sdist(sdist_directory: str, config_settings: dict | None = None) -> str:
    del config_settings
    sdist_name = f"{NAME}-{VERSION}.tar.gz"
    sdist_path = Path(sdist_directory) / sdist_name
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir) / f"{NAME}-{VERSION}"
        tmp_root.mkdir()
        for relative_path in [Path("pyproject.toml"), Path("README.md"), Path("build_backend.py")]:
            target = tmp_root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / relative_path).read_bytes())
        for source_path in _iter_package_files():
            target = tmp_root / source_path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source_path.read_bytes())
        with tarfile.open(sdist_path, "w:gz") as tar_file:
            tar_file.add(tmp_root, arcname=tmp_root.name)
    return sdist_name



def get_requires_for_build_wheel(config_settings: dict | None = None) -> list[str]:
    del config_settings
    return []



def get_requires_for_build_sdist(config_settings: dict | None = None) -> list[str]:
    del config_settings
    return []



def prepare_metadata_for_build_wheel(
    metadata_directory: str,
    config_settings: dict | None = None,
) -> str:
    del config_settings
    dist_info_dir = Path(metadata_directory) / DIST_INFO
    dist_info_dir.mkdir(parents=True, exist_ok=True)
    (dist_info_dir / "METADATA").write_text(_metadata_text(), encoding="utf-8")
    (dist_info_dir / "WHEEL").write_text(_wheel_text(), encoding="utf-8")
    entry_points_text = _entry_points_text()
    if entry_points_text:
        (dist_info_dir / "entry_points.txt").write_text(entry_points_text, encoding="utf-8")
    return DIST_INFO
