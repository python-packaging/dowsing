import unittest
from pathlib import Path

import volatile

from dowsing.setuptools import SetuptoolsReader
from dowsing.setuptools.setup_py_parsing import from_setup_py
from dowsing.types import Distribution


class SetuptoolsReaderTest(unittest.TestCase):
    def test_setup_cfg(self) -> None:
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

    def test_setup_py(self) -> None:
        with volatile.dir() as d:
            dp = Path(d)
            (dp / "setup.py").write_text(
                """\
from setuptools import setup
the_name = "foo"
setup(name=the_name, install_requires=["abc"], setup_requires=["def"])
"""
            )

            r = SetuptoolsReader(dp)
            self.assertEqual(("setuptools", "def"), r.get_requires_for_build_sdist())
            self.assertEqual(
                ("setuptools", "wheel", "def"), r.get_requires_for_build_wheel()
            )

    def _read(self, data: str) -> Distribution:
        with volatile.dir() as d:
            sp = Path(d, "setup.py")
            sp.write_text(data)
            return from_setup_py(Path(d), {})

    def test_smoke(self) -> None:
        d = self._read(
            """\
from setuptools import setup
setup(
    name="foo",
    version="0.1",
    classifiers=["CLASSIFIER"],
    install_requires=["abc"],
)
"""
        )
        self.assertEqual("foo", d.name)
        self.assertEqual("0.1", d.version)
        self.assertEqual(["CLASSIFIER"], d.classifiers)
        self.assertEqual(["abc"], d.requires_dist)
