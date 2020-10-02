import unittest
from pathlib import Path

import volatile
from highlighter.types import EnvironmentMarkers

from ..api import get_requires_for_build_sdist, get_requires_for_build_wheel


class ApiTest(unittest.TestCase):
    def test_all(self) -> None:
        with volatile.dir() as d:
            Path(d, "setup.py").write_text(
                """\
from setuptools import setup
setup(
    setup_requires=[
        "a; python_version < '3'", "b"],
    install_requires=[
        "c; python_version < '3'", "d"],
)
"""
            )
            env = EnvironmentMarkers.for_python("3.6.0")
            self.assertEqual(
                ["setuptools", "b"], get_requires_for_build_sdist(Path(d), env)
            )
            self.assertEqual(
                ["setuptools", "wheel", "b"], get_requires_for_build_wheel(Path(d), env)
            )
