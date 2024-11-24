import unittest
from pathlib import Path

import volatile

from dowsing.poetry import PoetryReader


class PoetryReaderTest(unittest.TestCase):
    def test_basic(self) -> None:
        with volatile.dir() as d:
            dp = Path(d)
            (dp / "pyproject.toml").write_text(
                """\
[build-system]
requires = ["poetry-core>=1.0.0a9"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "Name"
version = "1.5.2"
description = "Short Desc"
authors = ["Author <author@example.com>"]
license = "BSD-3-Clause"
homepage = "http://example.com"
classifiers = [
    "Not a real classifier",
]

[tool.poetry.dependencies]
python = "~2.7 || ^3.5"
functools32 = { version = "^3.2.3", python = "~2.7" }

[tool.poetry.urls]
"Bug Tracker" = "https://github.com/python-poetry/poetry/issues"
"""
            )
            r = PoetryReader(dp)
            md = r.get_metadata()
            self.assertEqual("Name", md.name)
            self.assertEqual("1.5.2", md.version)
            self.assertEqual("BSD-3-Clause", md.license)
            self.assertEqual(
                [
                    "homepage=http://example.com",
                    "Bug Tracker=https://github.com/python-poetry/poetry/issues",
                ],
                md.project_urls,
            )
            self.assertEqual(["Not a real classifier"], md.classifiers)
            self.assertEqual(["functools32"], md.requires_dist)
