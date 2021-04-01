import unittest
from configparser import RawConfigParser
from io import StringIO
from typing import Dict, List, Union

from imperfect import ConfigFile
from parameterized import parameterized

from dowsing.setuptools.types import (
    BoolWriter,
    DictWriter,
    ListCommaWriter,
    ListCommaWriterCompat,
    ListSemiWriter,
    SectionWriter,
    StrWriter,
)


class WriterTest(unittest.TestCase):
    @parameterized.expand(  # type: ignore
        [
            (False,),
            (True,),
        ]
    )
    def test_bool_writer(self, arg: bool) -> None:
        c = ConfigFile()
        c.set_value("a", "b", BoolWriter().to_ini(arg))
        buf = StringIO()
        c.build(buf)

        rcp = RawConfigParser(strict=False)
        rcp.read_string(buf.getvalue())
        self.assertEqual(str(arg).lower(), rcp["a"]["b"])

    @parameterized.expand(  # type: ignore
        [
            ("hello",),
            ("a\nb\nc",),
        ]
    )
    def test_str_writer(self, arg: str) -> None:
        c = ConfigFile()
        c.set_value("a", "b", StrWriter().to_ini(arg))
        buf = StringIO()
        c.build(buf)

        rcp = RawConfigParser(strict=False)
        rcp.read_string(buf.getvalue())
        self.assertEqual(arg, rcp["a"]["b"])

    @parameterized.expand(  # type: ignore
        [
            ([], ""),
            (["a"], "\na"),
            (["a", "b"], "\na\nb"),
            (["a", "b", "c"], "\na\nb\nc"),
        ]
    )
    def test_list_comma_writer(self, arg: List[str], expected: str) -> None:
        c = ConfigFile()
        c.set_value("a", "b", ListCommaWriter().to_ini(arg))
        buf = StringIO()
        c.build(buf)

        rcp = RawConfigParser(strict=False)
        rcp.read_string(buf.getvalue())
        self.assertEqual(expected, rcp["a"]["b"])

    @parameterized.expand(  # type: ignore
        [
            ([], ""),
            (["a"], "\na"),
            (["a", "b"], "\na\nb"),
            (["a", "b", "c"], "\na\nb\nc"),
        ]
    )
    def test_list_semi_writer(self, arg: List[str], expected: str) -> None:
        c = ConfigFile()
        c.set_value("a", "b", ListSemiWriter().to_ini(arg))
        buf = StringIO()
        c.build(buf)

        rcp = RawConfigParser(strict=False)
        rcp.read_string(buf.getvalue())
        self.assertEqual(expected, rcp["a"]["b"])

    @parameterized.expand(  # type: ignore
        # fmt: off
        [
            ({}, ""),
            ({"x": "y"}, "\nx=y"),
            ({"x": "y", "z": "zz"}, "\nx=y\nz=zz"),
        ]
        # fmt: on
    )
    def test_dict_writer(self, arg: Dict[str, str], expected: str) -> None:
        c = ConfigFile()
        c.set_value("a", "b", DictWriter().to_ini(arg))
        buf = StringIO()
        c.build(buf)

        rcp = RawConfigParser(strict=False)
        rcp.read_string(buf.getvalue())
        # I would prefer this be dangling lines
        self.assertEqual(expected, rcp["a"]["b"])

    @parameterized.expand(  # type: ignore
        # fmt: off
        [
            ([], ""),
            ("abc", "\nabc"),
            (["a"], "\na"),
            (["a", "b"], "\na\nb"),
            (["a", "b", "c"], "\na\nb\nc"),
        ]
        # fmt: on
    )
    def test_list_comma_writer_compat(
        self, arg: Union[str, List[str]], expected: str
    ) -> None:
        c = ConfigFile()
        c.set_value("a", "b", ListCommaWriterCompat().to_ini(arg))
        buf = StringIO()
        c.build(buf)

        rcp = RawConfigParser(strict=False)
        rcp.read_string(buf.getvalue())
        # I would prefer this be dangling lines
        self.assertEqual(expected, rcp["a"]["b"])

    @parameterized.expand(  # type: ignore
        [
            ([], ""),
            (["a"], "\na"),
            (["a", "b"], "\na\nb"),
            (["a", "b", "c"], "\na\nb\nc"),
        ]
    )
    def test_section_writer(self, arg: List[str], expected: str) -> None:
        c = ConfigFile()
        c.set_value("a", "b", SectionWriter().to_ini(arg))
        buf = StringIO()
        c.build(buf)

        rcp = RawConfigParser(strict=False)
        rcp.read_string(buf.getvalue())
        self.assertEqual(expected, rcp["a"]["b"])

    def test_roundtrip_str(self) -> None:
        s = "abc"
        inst = StrWriter()
        self.assertEqual(s, inst.from_ini(inst.to_ini(s)))

    def test_roundtrip_lists(self) -> None:
        lst = ["a", "bc"]
        inst = ListSemiWriter()
        self.assertEqual(lst, inst.from_ini(inst.to_ini(lst)))
        inst2 = ListCommaWriter()
        self.assertEqual(lst, inst2.from_ini(inst2.to_ini(lst)))
        inst3 = ListCommaWriterCompat()
        self.assertEqual(lst, inst3.from_ini(inst3.to_ini(lst)))

    def test_roundtrip_dict(self) -> None:
        d = {"a": "bc", "d": "ef"}
        inst = DictWriter()
        self.assertEqual(d, inst.from_ini(inst.to_ini(d)))

    def test_roundtrip_bool(self) -> None:
        for b in (True, False):
            inst = BoolWriter()
            self.assertEqual(b, inst.from_ini(inst.to_ini(b)))
