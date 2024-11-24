import unittest
from pathlib import Path
from typing import Dict, Optional

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

    def _read(
        self,
        data: str,
        src_dir: str = ".",
        extra_files: Optional[Dict[str, str]] = None,
    ) -> Distribution:
        with volatile.dir() as d:
            sp = Path(d, "setup.py")
            sp.write_text(data)
            if extra_files:
                for k, v in extra_files.items():
                    Path(d, k).write_text(v)
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

    def test_pbr_properly_enabled(self) -> None:
        d = self._read(
            """\
from setuptools import setup

setup(
    setup_requires=['pbr>=1.9', 'setuptools>=17.1'],
    pbr=True,
)""",
            extra_files={
                "setup.cfg": """\
[metadata]
name = pbr
author = OpenStack Foundation

[files]
packages =
    pkg
"""
            },
        )
        self.assertEqual(
            d.source_mapping,
            {
                "pkg/__init__.py": "pkg/__init__.py",
                "pkg/sub/__init__.py": "pkg/sub/__init__.py",
                "pkg/tests/__init__.py": "pkg/tests/__init__.py",
            },
        )

    def test_pbr_properly_enabled_src(self) -> None:
        d = self._read(
            """\
from setuptools import setup

setup(
    setup_requires=['pbr>=1.9', 'setuptools>=17.1'],
    pbr=True,
)""",
            src_dir="src",
            extra_files={
                "setup.cfg": """\
[metadata]
name = pbr
author = OpenStack Foundation

[files]
packages =
    pkg
packages_root = src
"""
            },
        )
        self.assertEqual(
            d.source_mapping,
            {
                "pkg/__init__.py": "src/pkg/__init__.py",
                "pkg/sub/__init__.py": "src/pkg/sub/__init__.py",
                "pkg/tests/__init__.py": "src/pkg/tests/__init__.py",
            },
        )

    def test_pbr_improperly_enabled(self) -> None:
        # pbr itself is something like this.
        d = self._read(
            """\
from setuptools import setup

setup()""",
            extra_files={
                "setup.cfg": """\
[metadata]
name = pbr
author = OpenStack Foundation

[files]
packages =
    pkg
"""
            },
        )
        self.assertEqual(
            d.source_mapping,
            {
                "pkg/__init__.py": "pkg/__init__.py",
                "pkg/sub/__init__.py": "pkg/sub/__init__.py",
                "pkg/tests/__init__.py": "pkg/tests/__init__.py",
            },
        )

    def test_add_items(self) -> None:
        d = self._read(
            """\
from setuptools import setup
a = "aaaa"
p = ["a", "b", "c"]
setup(name = a + "1111", packages=[] + p, classifiers=a + p)
            """
        )
        self.assertEqual(d.name, "aaaa1111")
        self.assertEqual(d.packages, ["a", "b", "c"])
        self.assertEqual(d.classifiers, "??")

    def test_self_reference_assignments(self) -> None:
        d = self._read(
            """\
from setuptools import setup

version = "base"
name = "foo"
name += "bar"
version = version + ".suffix"

classifiers = [
    "123",
    "abc",
]

if True:
    classifiers = classifiers + ["xyz"]

setup(
    name=name,
    version=version,
    classifiers=classifiers,
)
            """
        )
        self.assertEqual(d.name, "foobar")
        self.assertEqual(d.version, "base.suffix")
        self.assertSequenceEqual(d.classifiers, ["123", "abc", "xyz"])

    def test_circular_references(self) -> None:
        d = self._read(
            """\
from setuptools import setup

name = "foo"

foo = bar
bar = version
version = foo

classifiers = classifiers

setup(
    name=name,
    version=version,
)
            """
        )
        self.assertEqual(d.name, "foo")
        self.assertEqual(d.version, "??")
        self.assertEqual(d.classifiers, ())

    def test_redefines_builtin(self) -> None:
        d = self._read(
            """\
import setuptools
with open("CREDITS.txt", "r", encoding="utf-8") as fp:
    credits = fp.read()

long_desc = "a" + credits + "b"
name = "foo"

kwargs = dict(
    long_description = long_desc,
    name = name,
)

setuptools.setup(**kwargs)
"""
        )
        self.assertEqual(d.name, "foo")
        self.assertEqual(d.description, "??")
