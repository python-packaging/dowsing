from pathlib import Path
from typing import List

from highlighter.types import EnvironmentMarkers
from packaging.requirements import Requirement

from . import pep517


def get_requires_for_build_sdist(path: Path, env: EnvironmentMarkers) -> List[str]:
    reqs = pep517.get_requires_for_build_sdist(path)
    rv = []
    for req_str in reqs:
        req = Requirement(req_str)
        if req.marker is None or env.match(req.marker):
            rv.append(req_str)
    return rv


def get_requires_for_build_wheel(path: Path, env: EnvironmentMarkers) -> List[str]:
    reqs = pep517.get_requires_for_build_wheel(path)
    rv = []
    for req_str in reqs:
        req = Requirement(req_str)
        if req.marker is None or env.match(req.marker):
            rv.append(req_str)
    return rv


# TODO some kind of general get_requires
