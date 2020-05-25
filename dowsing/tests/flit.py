import unittest
from pathlib import Path

import volatile

from dowsing.flit import FlitReader


class FlitReaderTest(unittest.TestCase):
    def test_simplest(self):
        with volatile.dir() as d:
            dp = Path(d)
            (dp / "pyproject.toml").write_text(
                """\
[build-system]
backend = "flit_core.buildapi"
[tool.flit.metadata]
"""
            )

            # I assume this would be an error in flit, but we want to make sure we
            # handle missing metadata appropriately.

            r = FlitReader(dp)
            self.assertEqual((), r.get_requires_for_build_sdist())
            self.assertEqual((), r.get_requires_for_build_wheel())

    def test_normal(self):
        with volatile.dir() as d:
            dp = Path(d)
            (dp / "pyproject.toml").write_text(
                """\
[build-system]
requires = ["flit_core >=2,<4"]
backend = "flit_core.buildapi"

[tool.flit.metadata]
module = "foo"
requires = ["abc", "def"]
"""
            )

            r = FlitReader(dp)
            # Notably these do not include flit itself; that's handled by
            # dowsing.pep517
            self.assertEqual(["abc", "def"], r.get_requires_for_build_sdist())
            self.assertEqual(["abc", "def"], r.get_requires_for_build_wheel())
