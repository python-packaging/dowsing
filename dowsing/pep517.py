import importlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Type

import tomlkit

from .types import BaseReader

KNOWN_BACKENDS: Dict[str, str] = {
    "setuptools.build_meta:__legacy__": "dowsing.setuptools:SetuptoolsReader",
    "setuptools.build_meta": "dowsing.setuptools:SetuptoolsReader",
    "flit_core.buildapi": "dowsing.flit:FlitReader",
}


def get_backend(path: Path) -> Tuple[List[str], BaseReader]:
    pyproject = path / "pyproject.toml"
    backend = "setuptools.build_meta:__legacy__"
    requires: List[str] = []
    if pyproject.exists():
        doc = tomlkit.parse(pyproject.read_text())
        if "build-system" in doc:
            # 1b. include any build-system requires
            if "requires" in doc["build-system"]:
                requires.extend(doc["build-system"]["requires"])
            if "build-backend" in doc["build-system"]:
                backend = doc["build-system"]["build-backend"]
            # TODO backend-path

    try:
        backend_path = KNOWN_BACKENDS[backend]
    except KeyError:
        raise Exception(f"Unknown pep517 backend {backend!r}")

    mod, _, x = backend_path.partition(":")
    cls: Type[BaseReader] = getattr(importlib.import_module(mod), x)

    return requires, cls(path)


def get_requires_for_build_sdist(path: Path):
    # TODO config_settings, env

    requires, backend = get_backend(path)

    return requires + list(backend.get_requires_for_build_sdist())


def get_requires_for_build_wheel(path: Path):
    # TODO config_settings, env

    requires, backend = get_backend(path)
    return requires + list(backend.get_requires_for_build_wheel())


def get_metadata(path: Path):
    # TODO config_settings, env

    _, backend = get_backend(path)
    return backend.get_metadata()


def main(path: Path):
    d = {
        "get_requires_for_build_sdist": get_requires_for_build_sdist(path),
        "get_requires_for_build_wheel": get_requires_for_build_wheel(path),
        "get_metadata": get_metadata(path).asdict(),
    }
    print(json.dumps(d))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
