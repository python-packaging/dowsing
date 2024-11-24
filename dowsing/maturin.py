from pathlib import Path
from typing import Sequence

import tomlkit

from .types import BaseReader, Distribution


class MaturinReader(BaseReader):
    def __init__(self, path: Path):
        self.path = path

    def get_requires_for_build_sdist(self) -> Sequence[str]:
        return []  # TODO

    def get_requires_for_build_wheel(self) -> Sequence[str]:
        return []  # TODO

    def get_metadata(self) -> Distribution:
        pyproject = self.path / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())

        d = Distribution()
        d.metadata_version = "2.1"

        cargo = self.path / "Cargo.toml"
        doc = tomlkit.parse(cargo.read_text())
        package = doc.get("package", {})
        for k, v in package.items():
            if k == "name":
                d.name = v
            elif k == "version":
                d.version = v
            elif k == "license":
                d.license = v
            elif k == "description":
                d.summary = v
            # authors ["foo <foo@foo.com>"]
            # repository
            # homepage
            # readme (filename)

        maturin = package.get("metadata", {}).get("maturin", {})
        for k, v in maturin.items():
            if k == "requires-python":
                d.requires_python = v
            elif k == "classifier":
                d.classifiers = v
            elif k == "requires-dist":
                d.requires_dist = v
            # Many others, see https://docs.rs/maturin/0.8.3/maturin/struct.Metadata21.html
            # but these do not seem to be that popular.

        return d
