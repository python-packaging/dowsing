from pathlib import Path
from typing import Sequence

import tomlkit

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

        for k, v in doc["tool"]["flit"]["metadata"].items():
            k2 = k.replace("-", "_")
            if k2 in d:
                setattr(d, k2, v)

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
