from pathlib import Path
from typing import Sequence

import tomlkit
from setuptools import find_packages

from .types import BaseReader, Distribution


class FlitReader(BaseReader):
    def __init__(self, path: Path):
        self.path = path

    def get_requires_for_build_sdist(self) -> Sequence[str]:
        return self._get_requires()

    def get_requires_for_build_wheel(self) -> Sequence[str]:
        return self._get_requires()

    def get_metadata(self) -> Distribution:
        pyproject = self.path / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())

        d = Distribution()
        d.metadata_version = "2.1"
        d.project_urls = {}

        for k, v in doc["tool"]["flit"]["metadata"].items():
            # TODO description-file -> long_description
            # TODO home-page -> urls
            # TODO requires -> requires_dist
            # TODO tool.flit.metadata.urls
            if k == "home-page":
                d.project_urls["Homepage"] = v
                continue
            elif k == "module":
                k = "packages"
                v = find_packages(self.path.as_posix(), include=(f"{v}.*"))
                d.packages_dict = {i: i.replace(".", "/") for i in v}
            elif k == "description-file":
                k = "description"
                v = f"file: {v}"
            elif k == "requires":
                k = "requires_dist"

            k2 = k.replace("-", "_")
            if k2 in d:
                setattr(d, k2, v)

        for k, v in doc["tool"]["flit"]["metadata"].get("urls", {}).items():
            d.project_urls[k] = v

        # TODO extras-require

        return d

    def _get_requires(self) -> Sequence[str]:
        """
        Flit considers all requirements to be build-time requirements because of
        how it extracts versions. This seems prone to making cycles where you
        can't bootstrap exclusively from source...

        https://github.com/takluyver/flit/issues/141
        """
        pyproject = self.path / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())
        seq = doc["tool"]["flit"]["metadata"].get("requires", ())
        assert isinstance(seq, (list, tuple))
        return seq
