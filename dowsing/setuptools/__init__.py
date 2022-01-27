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

        # This is the bare minimum to get pbr projects to show as having any
        # sources.  I don't want to use pbr.util.cfg_to_args because it appears
        # to import and run arbitrary code.
        if d1.pbr or (d1.pbr__files__packages and not d1.packages):
            where = "."
            if d1.pbr__files__packages_root:
                d1.package_dir = {"": d1.pbr__files__packages_root}
                where = d1.pbr__files__packages_root

            if d1.pbr__files__packages:
                d1.packages = d1.pbr__files__packages
            else:
                d1.packages = FindPackages(where, (), ("*",))  # type: ignore

        # package_dir can both add and remove components, see docs
        # https://docs.python.org/2/distutils/setupscript.html#listing-whole-packages
        package_dir: Mapping[str, str] = d1.package_dir
        # If there was an error, we might have written "??"
        if package_dir != "??":  # type: ignore
            if not package_dir:
                package_dir = {"": "."}

            assert isinstance(package_dir, dict)

            def mangle(package: str) -> str:
                for x, rest in _prefixes(package):
                    if x in package_dir:
                        return posixpath.normpath(posixpath.join(package_dir[x], rest))

                # Some projects seem to set only a partial package_dir, but then
                # use find_packages which wants to include some outside.
                return package

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
            elif d1.packages not in ("??", "????"):
                assert isinstance(
                    d1.packages, (list, tuple)
                ), f"{d1.packages!r} is not a list/tuple"
                for p in d1.packages:
                    if p:
                        d1.packages_dict[p] = mangle(p)

        d1.source_mapping = d1._source_mapping(self.path)
        return d1

    def _get_requires(self) -> Tuple[str, ...]:
        dist = self.get_metadata()
        return tuple(dist.setup_requires)
