import unittest
from pathlib import Path

import volatile

from dowsing.setuptools import SetuptoolsReader
from dowsing.setuptools.types import (
    BoolWriter,
    DictWriter,
    ListCommaWriter,
    ListCommaWriterCompat,
    ListSemiWriter,
    StrWriter,
)


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

    def test_writer_classes_roundtrip_str(self) -> None:
        s = "abc"
        inst = StrWriter()
        self.assertEqual(s, inst.from_ini(inst.to_ini(s)))

    def test_writer_classes_roundtrip_lists(self) -> None:
        lst = ["a", "bc"]
        inst = ListSemiWriter()
        self.assertEqual(lst, inst.from_ini(inst.to_ini(lst)))
        inst2 = ListCommaWriter()
        self.assertEqual(lst, inst2.from_ini(inst2.to_ini(lst)))
        inst3 = ListCommaWriterCompat()
        self.assertEqual(lst, inst3.from_ini(inst3.to_ini(lst)))

    def test_writer_classes_roundtrip_dict(self) -> None:
        d = {"a": "bc", "d": "ef"}
        inst = DictWriter()
        self.assertEqual(d, inst.from_ini(inst.to_ini(d)))

    def test_writer_classes_roundtrip_bool(self) -> None:
        for b in (True, False):
            inst = BoolWriter()
            self.assertEqual(b, inst.from_ini(inst.to_ini(b)))
