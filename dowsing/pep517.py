import importlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Type

import tomlkit

from .types import BaseReader, Distribution

KNOWN_BACKENDS: Dict[str, str] = {
    "setuptools.build_meta:__legacy__": "dowsing.setuptools:SetuptoolsReader",
    "setuptools.build_meta": "dowsing.setuptools:SetuptoolsReader",
    "jupyter_packaging.build_api": "dowsing.setuptools:SetuptoolsReader",
    "flit_core.buildapi": "dowsing.flit:FlitReader",
    "flit.buildapi": "dowsing.flit:FlitReader",
    "maturin": "dowsing.maturin:MaturinReader",
    "poetry.core.masonry.api": "dowsing.poetry:PoetryReader",
    "poetry.masonry.api": "dowsing.poetry:PoetryReader",
}


def get_backend(path: Path) -> Tuple[List[str], BaseReader]:
    pyproject = path / "pyproject.toml"
    backend = "setuptools.build_meta:__legacy__"
    # TODO for setuptools, we should also include requirements
    requires: List[str] = []
    if pyproject.exists():
        doc = tomlkit.parse(pyproject.read_text())
        table = doc.get("build-system", {})

        # 1b. include any build-system requires
        if "requires" in table:
            requires.extend(table["requires"])
        if "build-backend" in table:
            backend = table["build-backend"]
        # TODO backend-path

    try:
        backend_path = KNOWN_BACKENDS[backend]
    except KeyError:
        raise Exception(f"Unknown pep517 backend {backend!r}")

    mod, _, x = backend_path.partition(":")
    cls: Type[BaseReader] = getattr(importlib.import_module(mod), x)

    return requires, cls(path)


def get_requires_for_build_sdist(path: Path) -> List[str]:
    # TODO config_settings, env

    requires, backend = get_backend(path)

    return requires + list(backend.get_requires_for_build_sdist())


def get_requires_for_build_wheel(path: Path) -> List[str]:
    # TODO config_settings, env

    requires, backend = get_backend(path)
    return requires + list(backend.get_requires_for_build_wheel())


def get_metadata(path: Path) -> Distribution:
    # TODO config_settings, env

    _, backend = get_backend(path)
    return backend.get_metadata()


def _default(obj: Any) -> Any:
    if obj.__class__.__name__ == "FindPackages":
        return f"FindPackages({obj.where!r}, {obj.exclude!r}, {obj.include!r}"
    raise TypeError(obj)


def main(path: Path) -> None:
    metadata = get_metadata(path)
    d = {
        "get_requires_for_build_sdist": get_requires_for_build_sdist(path),
        "get_requires_for_build_wheel": get_requires_for_build_wheel(path),
        "get_metadata": metadata.asdict(),
        "source_mapping": metadata.source_mapping,
    }
    print(json.dumps(d, default=_default))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
