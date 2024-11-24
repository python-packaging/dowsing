from pathlib import Path
from typing import Sequence

import tomlkit
from setuptools import find_packages

from .pep621 import Pep621Reader
from .types import Distribution


class FlitReader(Pep621Reader):
    def __init__(self, path: Path):
        self.path = path

    def get_requires_for_build_sdist(self) -> Sequence[str]:
        return self._get_requires()

    def get_requires_for_build_wheel(self) -> Sequence[str]:
        return self._get_requires()

    def get_metadata(self) -> Distribution:
        pyproject = self.path / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())

        d = self.get_pep621_metadata()
        d.entry_points = dict(d.entry_points) or {}
        d.project_urls = list(d.project_urls)

        assert isinstance(d.project_urls, list)

        flit = doc.get("tool", {}).get("flit", {})
        metadata = flit.get("metadata", {})
        for k, v in metadata.items():
            # TODO description-file -> long_description
            # TODO home-page -> urls
            # TODO requires -> requires_dist
            # TODO tool.flit.metadata.urls
            if k == "home-page":
                d.project_urls.append("Homepage={v}")
                continue
            elif k == "module":
                if (self.path / f"{v}.py").exists():
                    k = "py_modules"
                    v = [v]
                else:
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

        for k, v in metadata.get("urls", {}).items():
            d.project_urls.append(f"{k}={v}")

        for k, v in flit.get("scripts", {}).items():
            d.entry_points[k] = v

        # TODO extras-require
        # TODO distutils commands (e.g. pex 2.1.19)

        d.source_mapping = d._source_mapping(self.path)
        return d

    def _get_requires(self) -> Sequence[str]:
        """
        Flit considers all requirements to be build-time requirements because of
        how it extracts versions. This seems prone to making cycles where you
        can't bootstrap exclusively from source...

        https://github.com/takluyver/flit/issues/141
        """
        dist = self.get_metadata()
        seq = dist.requires_dist
        assert isinstance(seq, (list, tuple))
        return seq
