import unittest
from pathlib import Path

import volatile

from ..flit import FlitReader
from ..pep517 import get_backend
from ..setuptools import SetuptoolsReader


class Pep517Test(unittest.TestCase):
    def test_no_backend(self) -> None:
        with volatile.dir() as d:
            dp = Path(d)
            requires, inst = get_backend(dp)
            # self.assertEqual(["setuptools"], requires)
            self.assertIsInstance(inst, SetuptoolsReader)

    def test_setuptools_backend(self) -> None:
        with volatile.dir() as d:
            dp = Path(d)
            Path(d, "pyproject.toml").write_text("")
            requires, inst = get_backend(dp)
            # self.assertEqual(["setuptools"], requires)
            self.assertIsInstance(inst, SetuptoolsReader)

    def test_flit_backend(self) -> None:
        with volatile.dir() as d:
            dp = Path(d)
            Path(d, "pyproject.toml").write_text(
                """\
[build-system]
requires = ["flit_core >=2,<4"]
build-backend = "flit_core.buildapi"
"""
            )
            requires, inst = get_backend(dp)
            self.assertEqual(["flit_core >=2,<4"], requires)
            self.assertIsInstance(inst, FlitReader)
