import unittest
from pathlib import Path

import volatile

from dowsing.setuptools import SetuptoolsReader
from dowsing.setuptools.setup_py_parsing import FindPackages
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

    def test_setup_cfg_dash_normalization(self) -> None:
        # I can't find documentation for this, but e.g. auditwheel 3.2.0 uses
        # dashes instead of underscores and it works.
        with volatile.dir() as d:
            dp = Path(d)
            (dp / "setup.cfg").write_text(
                """\
[metadata]
name = foo
author = Foo
author-email = foo@example.com
"""
            )

            r = SetuptoolsReader(dp)
            md = r.get_metadata()
            self.assertEqual("foo@example.com", md.author_email)

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

    def _read(self, data: str, src_dir: str = ".") -> Distribution:
        with volatile.dir() as d:
            sp = Path(d, "setup.py")
            sp.write_text(data)
            Path(d, src_dir, "pkg").mkdir(parents=True)
            Path(d, src_dir, "pkg", "__init__.py").touch()
            Path(d, src_dir, "pkg", "sub").mkdir()
            Path(d, src_dir, "pkg", "sub", "__init__.py").touch()
            Path(d, src_dir, "pkg", "tests").mkdir()
            Path(d, src_dir, "pkg", "tests", "__init__.py").touch()
            return SetuptoolsReader(Path(d)).get_metadata()

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

    def test_packages_dict_literal(self) -> None:
        d = self._read(
            """\
from setuptools import setup, find_packages
setup(
    packages=["pkg", "pkg.tests"],
)
"""
        )
        self.assertEqual(d.packages, ["pkg", "pkg.tests"])
        self.assertEqual(d.packages_dict, {"pkg": "pkg", "pkg.tests": "pkg/tests"})

    def test_packages_find_packages_call(self) -> None:
        d = self._read(
            """\
from setuptools import setup, find_packages
setup(
    packages=find_packages(exclude=("pkg.sub",)),
)
        """
        )
        self.assertEqual(d.packages, FindPackages(".", ("pkg.sub",), ("*",)))
        self.assertEqual(d.packages_dict, {"pkg": "pkg", "pkg.tests": "pkg/tests"})

    def test_packages_find_packages_call_package_dir(self) -> None:
        d = self._read(
            """\
from setuptools import setup, find_packages
setup(
    package_dir={'': '.'},
    packages=find_packages(exclude=("pkg.sub",)),
)
        """
        )
        self.assertEqual(d.packages, FindPackages(".", ("pkg.sub",), ("*",)))
        self.assertEqual(d.packages_dict, {"pkg": "pkg", "pkg.tests": "pkg/tests"})

    def test_packages_find_packages_call_package_dir_src(self) -> None:
        d = self._read(
            """\
from setuptools import setup, find_packages
setup(
    package_dir={'': 'src'},
    packages=find_packages("src", exclude=("pkg.sub",)),
)
        """,
            "src",
        )
        self.assertEqual(d.packages, FindPackages("src", ("pkg.sub",), ("*",)))
        self.assertEqual(
            d.packages_dict, {"pkg": "src/pkg", "pkg.tests": "src/pkg/tests"}
        )

    def test_packages_find_packages_call_package_dir2(self) -> None:
        d = self._read(
            """\
from setuptools import setup, find_packages
setup(
    package_dir={'pkg': 'pkg'},
    packages=find_packages(exclude=("pkg.sub",)),
)
        """
        )
        self.assertEqual(d.packages, FindPackages(".", ("pkg.sub",), ("*",)))
        self.assertEqual(d.packages_dict, {"pkg": "pkg", "pkg.tests": "pkg/tests"})
        self.assertEqual(
            d.source_mapping,
            {
                "pkg/__init__.py": "pkg/__init__.py",
                # TODO this line should not be here as it's excluded
                "pkg/sub/__init__.py": "pkg/sub/__init__.py",
                "pkg/tests/__init__.py": "pkg/tests/__init__.py",
            },
        )

    def test_packages_find_packages_call_package_dir3(self) -> None:
        d = self._read(
            """\
from setuptools import setup, find_packages
setup(
    package_dir={'': 'pkg'},
    packages=find_packages("pkg"),
)
        """
        )
        self.assertEqual(d.packages, FindPackages("pkg", (), ("*",)))
        self.assertEqual(d.packages_dict, {"sub": "pkg/sub", "tests": "pkg/tests"})
        self.assertEqual(
            d.source_mapping,
            {
                "sub/__init__.py": "pkg/sub/__init__.py",
                "tests/__init__.py": "pkg/tests/__init__.py",
            },
        )

    def test_packages_find_packages_include(self) -> None:
        # This is weird behavior but documented.
        d = self._read(
            """\
from setuptools import setup, find_packages
setup(
    packages=find_packages(include=("pkg",)),
)
        """
        )
        self.assertEqual(d.packages, FindPackages(".", (), ("pkg",)))
        self.assertEqual(d.packages_dict, {"pkg": "pkg"})
        # TODO strict interpretation should be this commented line
        # self.assertEqual(d.source_mapping, {"pkg/__init__.py": "pkg/__init__.py"})
        self.assertEqual(
            d.source_mapping,
            {
                "pkg/__init__.py": "pkg/__init__.py",
                "pkg/sub/__init__.py": "pkg/sub/__init__.py",
                "pkg/tests/__init__.py": "pkg/tests/__init__.py",
            },
        )

    def test_py_modules(self) -> None:
        d = self._read(
            """\
from setuptools import setup, find_packages
setup(
    py_modules=["a", "b"],
)
        """
        )
        self.assertEqual(d.source_mapping, {"a.py": "a.py", "b.py": "b.py"})

    def test_invalid_packages(self) -> None:
        d = self._read(
            """\
from setuptools import setup, find_packages
setup(
    packages = ["zzz"],
)
        """
        )
        # TODO wish this were None
        self.assertEqual(d.source_mapping, {})
