import unittest
from pathlib import Path

import volatile

from dowsing.maturin import MaturinReader


class MaturinReaderTest(unittest.TestCase):
    def test_orjson(self) -> None:
        # This is a simplified version of orjson 3.4.0
        with volatile.dir() as d:
            dp = Path(d)
            (dp / "pyproject.toml").write_text(
                """\
[project]
name = "orjson"
repository = "https://example.com/"

[build-system]
build-backend = "maturin"
requires = ["maturin>=0.8.1,<0.9"]
"""
            )

            (dp / "Cargo.toml").write_text(
                """\
[package]
name = "orjson"
version = "3.4.0"
authors = ["foo <foo@example.com>"]
description = "Summary here"
license = "Apache-2.0 OR MIT"
repository = "https://example.com/repo"
homepage = "https://example.com/home"
readme = "README.md"
keywords = ["foo", "bar", "baz"]

[package.metadata.maturin]
requires-python = ">=3.6"
classifer = [
    "License :: OSI Approved :: Apache Software License",
    "License :: OSI Approved :: MIT License",
]
"""
            )
            r = MaturinReader(dp)
            md = r.get_metadata()
            self.assertEqual("orjson", md.name)
            self.assertEqual("3.4.0", md.version)
            # TODO more tests
