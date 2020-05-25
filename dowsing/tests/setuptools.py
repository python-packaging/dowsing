import unittest
from pathlib import Path

import volatile

from dowsing.setuptools import SetuptoolsReader


class SetuptoolsReaderTest(unittest.TestCase):
    def test_setup_cfg(self):
        with volatile.dir() as d:
            dp = Path(d)
            (dp / "setup.cfg").write_text(
                """\
[metadata]
name = foo
[options]
install_requires = abc
setup_requires = def
"""
            )

            r = SetuptoolsReader(dp)
            self.assertEqual(("setuptools", "def"), r.get_requires_for_build_sdist())
            self.assertEqual(
                ("setuptools", "wheel", "def"), r.get_requires_for_build_wheel()
            )

    def test_setup_py(self):
        with volatile.dir() as d:
            dp = Path(d)
            (dp / "setup.py").write_text(
                """\
from setuptools import setup
setup(name="foo", install_requires=["abc"], setup_requires=["def"])
"""
            )

            r = SetuptoolsReader(dp)
            self.assertEqual(("setuptools", "def"), r.get_requires_for_build_sdist())
            self.assertEqual(
                ("setuptools", "wheel", "def"), r.get_requires_for_build_wheel()
            )
