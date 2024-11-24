import unittest
from pathlib import Path

import volatile

from ..pep621 import Pep621Reader


class Pep621ReaderTest(unittest.TestCase):
    def test_simplest(self) -> None:
        with volatile.dir() as d:
            dp = Path(d)
            (dp / "pyproject.toml").write_text(
                """\
[project]
name = "Name"
"""
            )

            r = Pep621Reader(dp)
            md = r.get_pep621_metadata()
            self.assertEqual("Name", md.name)

    def test_normal(self) -> None:
        with volatile.dir() as d:
            dp = Path(d)
            (dp / "pyproject.toml").write_text(
                """\
[project]
name = "foo"
dependencies = ["abc", "def"]
license = {text = "MIT"}

[project.urls]
Foo = "https://"
"""
            )
            (dp / "foo").mkdir()
            (dp / "foo" / "tests").mkdir()
            (dp / "foo" / "__init__.py").write_text("")
            (dp / "foo" / "tests" / "__init__.py").write_text("")

            r = Pep621Reader(dp)
            md = r.get_pep621_metadata()
            self.assertEqual("foo", md.name)
            self.assertEqual(
                {
                    "metadata_version": "2.1",
                    "name": "foo",
                    "license": "MIT",
                    "packages": ["foo", "foo.tests"],
                    "packages_dict": {"foo": "foo", "foo.tests": "foo/tests"},
                    "requires_dist": ["abc", "def"],
                    "project_urls": ["Foo=https://"],
                },
                md.asdict(),
            )

    def test_pep639(self) -> None:
        with volatile.dir() as d:
            dp = Path(d)
            (dp / "pyproject.toml").write_text(
                """\
[project]
name = "Name"
license = "MIT"
"""
            )

            r = Pep621Reader(dp)
            md = r.get_pep621_metadata()
            self.assertEqual("Name", md.name)
            self.assertEqual("MIT", md.license)
