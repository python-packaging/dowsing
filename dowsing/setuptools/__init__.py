import posixpath
from pathlib import Path
from typing import Generator, Mapping, Sequence, Tuple

from setuptools import find_packages

from ..types import BaseReader, Distribution
from .setup_cfg_parsing import from_setup_cfg
from .setup_py_parsing import FindPackages, from_setup_py


def _prefixes(dotted_name: str) -> Generator[Tuple[str, str], None, None]:
    parts = dotted_name.split(".")
    for i in range(len(parts), -1, -1):
        yield ".".join(parts[:i]), "/".join(parts[i:])


class SetuptoolsReader(BaseReader):
    def __init__(self, path: Path):
        self.path = path

    def get_requires_for_build_sdist(self) -> Sequence[str]:
        # TODO the documented behavior of pip (setuptools with a version
        # constraint) and what the pep517 module's build.compat_system does
        # differ.
        #
        # https://pip.pypa.io/en/stable/reference/pip/#pep-517-and-518-support
        # https://github.com/pypa/pep517/blob/master/pep517/build.py
        return ("setuptools",) + self._get_requires()

    def get_requires_for_build_wheel(self) -> Sequence[str]:
        return ("setuptools", "wheel") + self._get_requires()

    def get_metadata(self) -> Distribution:
        if (self.path / "setup.cfg").exists():
            d1 = from_setup_cfg(self.path, {})
        else:
            d1 = Distribution()

        if (self.path / "setup.py").exists():
            d2 = from_setup_py(self.path, {})
            for k in d2:
                if getattr(d2, k):
                    setattr(d1, k, getattr(d2, k))

        # package_dir can both add and remove components, see docs
        # https://docs.python.org/2/distutils/setupscript.html#listing-whole-packages
        package_dir: Mapping[str, str] = d1.package_dir
        # If there was an error, we might have written "??"
        if package_dir != "??":
            if not package_dir:
                package_dir = {"": "."}

            assert isinstance(package_dir, dict)

            def mangle(package: str) -> str:
                for x, rest in _prefixes(package):
                    if x in package_dir:
                        return posixpath.normpath(posixpath.join(package_dir[x], rest))
                raise Exception("Should have stopped by now")

            d1.packages_dict = {}  # Break shared class-level dict

            # The following as_posix calls are necessary for Windows, but don't
            # hurt elsewhere.
            if isinstance(d1.packages, FindPackages):
                # This encodes a lot of sketchy logic, and deserves more test cases,
                # plus some around py_modules
                for p in find_packages(
                    (self.path / d1.packages.where).as_posix(),
                    d1.packages.exclude,
                    d1.packages.include,
                ):
                    d1.packages_dict[p] = mangle(p)
            elif d1.packages == ["find:"]:
                for p in find_packages(
                    (self.path / d1.find_packages_where).as_posix(),
                    d1.find_packages_exclude,
                    d1.find_packages_include,
                ):
                    d1.packages_dict[p] = mangle(p)
            elif d1.packages != "??":
                assert isinstance(d1.packages, (list, tuple))
                for p in d1.packages:
                    d1.packages_dict[p] = mangle(p)

        d1.source_mapping = d1._source_mapping(self.path)
        return d1

    def _get_requires(self) -> Tuple[str, ...]:
        dist = self.get_metadata()
        return tuple(dist.setup_requires)
