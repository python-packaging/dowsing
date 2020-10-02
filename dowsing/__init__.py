# TODO:
# - document how this is inspired by pep 517
# - simulated env, e.g. what would the requirements be on py2
# - when merging various requires, call out where they're from.
# - find the cst node that setup.py uses to add a certain kwarg
# - imports (definitely/possible[an if/catch importerror])

from .api import get_requires_for_build_sdist, get_requires_for_build_wheel

__all__ = ["get_requires_for_build_sdist", "get_requires_for_build_wheel"]
