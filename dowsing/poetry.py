import posixpath
from pathlib import Path
from typing import Sequence

import tomlkit
from setuptools import find_packages

from .types import BaseReader, Distribution

METADATA_MAPPING = {
    "name": "name",
    "version": "version",
    "description": "summary",
    "license": "license",  # SPDX short name
    # authors
    # maintainers
    # readme -> long desc? w/ content type rst/md
    "keywords": "keywords",
    "classifiers": "classifiers",
}


class PoetryReader(BaseReader):
    def __init__(self, path: Path):
        self.path = path

    def get_requires_for_build_sdist(self) -> Sequence[str]:
        return ()  # TODO

    def get_requires_for_build_wheel(self) -> Sequence[str]:
        return ()  # TODO

    def get_metadata(self) -> Distribution:
        pyproject = self.path / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())

        d = Distribution()
        d.metadata_version = "2.1"
        d.project_urls = []
        d.entry_points = {}
        d.requires_dist = []
        d.packages = []
        d.packages_dict = {}

        assert isinstance(d.project_urls, list)

        poetry = doc.get("tool", {}).get("poetry", {})
        for k, v in poetry.items():
            if k in ("homepage", "repository", "documentation"):
                d.project_urls.append(f"{k}={v}")
            elif k == "packages":
                # TODO improve and add tests; this works for tf2_utils and
                # poetry itself but include can be a glob and there are excludes
                for x in v:
                    f = x.get("from", ".")
                    for p in find_packages((self.path / f).as_posix()):
                        if p == x["include"] or p.startswith(f"{x['include']}."):
                            d.packages_dict[p] = posixpath.normpath(
                                posixpath.join(f, p.replace(".", "/"))
                            )
                            d.packages.append(p)
            elif k in METADATA_MAPPING:
                setattr(d, METADATA_MAPPING[k], v)

        if not d.packages:
            for p in find_packages(self.path.as_posix()):
                d.packages_dict[p] = p.replace(".", "/")
                d.packages.append(p)

        for k, v in poetry.get("dependencies", {}).items():
            if k == "python":
                pass  # TODO translate to requires_python
            else:
                d.requires_dist.append(k)  # TODO something with version

        for k, v in poetry.get("urls", {}).items():
            d.project_urls.append(f"{k}={v}")

        for k, v in poetry.get("scripts", {}).items():
            d.entry_points[k] = v

        d.source_mapping = d._source_mapping(self.path)
        return d
