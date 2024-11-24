import unittest
from pathlib import Path

import volatile

from dowsing.flit import FlitReader


class FlitReaderTest(unittest.TestCase):
    def test_simplest(self) -> None:
        with volatile.dir() as d:
            dp = Path(d)
            (dp / "pyproject.toml").write_text(
                """\
[build-system]
build-backend = "flit_core.buildapi"
[tool.flit.metadata]
name = "Name"
"""
            )

            # I assume this would be an error in flit, but we want to make sure we
            # handle missing metadata appropriately.

            r = FlitReader(dp)
            self.assertEqual([], r.get_requires_for_build_sdist())
            self.assertEqual([], r.get_requires_for_build_wheel())
            md = r.get_metadata()
            self.assertEqual("Name", md.name)

    def test_normal(self) -> None:
        with volatile.dir() as d:
            dp = Path(d)
            (dp / "pyproject.toml").write_text(
                """\
[build-system]
requires = ["flit_core >=2,<4"]
build-backend = "flit_core.buildapi"

[tool.flit.metadata]
name = "Name"
module = "foo"
requires = ["abc", "def"]

[tool.flit.metadata.urls]
Foo = "https://"
"""
            )
            (dp / "foo").mkdir()
            (dp / "foo" / "tests").mkdir()
            (dp / "foo" / "__init__.py").write_text("")
            (dp / "foo" / "tests" / "__init__.py").write_text("")

            r = FlitReader(dp)
            # Notably these do not include flit itself; that's handled by
            # dowsing.pep517
            self.assertEqual(["abc", "def"], r.get_requires_for_build_sdist())
            self.assertEqual(["abc", "def"], r.get_requires_for_build_wheel())
            md = r.get_metadata()
            self.assertEqual("Name", md.name)
            self.assertEqual(
                {
                    "metadata_version": "2.1",
                    "name": "Name",
                    "packages": ["foo", "foo.tests"],
                    "packages_dict": {"foo": "foo", "foo.tests": "foo/tests"},
                    "requires_dist": ["abc", "def"],
                    "project_urls": ["Foo=https://"],
                },
                md.asdict(),
            )

    def test_pep621(self) -> None:
        with volatile.dir() as d:
            dp = Path(d)
            (dp / "pyproject.toml").write_text(
                """\
[build-system]
requires = ["flit_core >=2,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "foo"
dependencies = ["abc", "def"]

[project.urls]
Foo = "https://"
"""
            )
            (dp / "foo").mkdir()
            (dp / "foo" / "tests").mkdir()
            (dp / "foo" / "__init__.py").write_text("")
            (dp / "foo" / "tests" / "__init__.py").write_text("")

            r = FlitReader(dp)
            # Notably these do not include flit itself; that's handled by
            # dowsing.pep517
            self.assertEqual(["abc", "def"], r.get_requires_for_build_sdist())
            self.assertEqual(["abc", "def"], r.get_requires_for_build_wheel())
            md = r.get_metadata()
            self.assertEqual("foo", md.name)
            self.assertEqual(
                {
                    "metadata_version": "2.1",
                    "name": "foo",
                    "packages": ["foo", "foo.tests"],
                    "packages_dict": {"foo": "foo", "foo.tests": "foo/tests"},
                    "requires_dist": ["abc", "def"],
                    "project_urls": ["Foo=https://"],
                },
                md.asdict(),
            )
