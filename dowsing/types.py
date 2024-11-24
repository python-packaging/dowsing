from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional, Sequence, Set, Tuple

import pkginfo.distribution


class BaseReader:
    """
    Base class for reading metadata.
    """

    def __init__(self, path: Path):
        self.path = path

    def get_requires_for_build_sdist(self) -> Sequence[str]:
        """
        Equivalent to the pep517 api.
        """
        raise NotImplementedError

    def get_requires_for_build_wheel(self) -> Sequence[str]:
        """
        Equivalent to the pep517 api.
        """
        raise NotImplementedError

    def get_metadata(self) -> "Distribution":
        """
        Gets a Distribution object with the metadata.

        Closer to pkginfo (it uses a subclass) than what you would get just by
        using email.parser.
        """
        raise NotImplementedError


DEFAULT_EMPTY_DICT: Mapping[str, Any] = MappingProxyType({})


class Distribution(pkginfo.distribution.Distribution):
    # These are not actually part of the metadata, see PEP 566
    setup_requires: Sequence[str] = ()
    tests_require: Sequence[str] = ()
    extras_require: Mapping[str, Sequence[str]] = DEFAULT_EMPTY_DICT
    use_scm_version: Optional[bool] = None
    zip_safe: Optional[bool] = None
    include_package_data: Optional[bool] = None
    test_suite: str = ""
    test_loader: str = ""
    namespace_packages: Sequence[str] = ()
    package_data: Mapping[str, Sequence[str]] = DEFAULT_EMPTY_DICT
    packages: Sequence[str] = ()
    package_dir: Mapping[str, str] = DEFAULT_EMPTY_DICT
    packages_dict: Mapping[str, str] = DEFAULT_EMPTY_DICT
    py_modules: Sequence[str] = ()
    entry_points: Mapping[str, Sequence[str]] = DEFAULT_EMPTY_DICT
    find_packages_where: str = "."
    find_packages_exclude: Sequence[str] = ()
    find_packages_include: Sequence[str] = ("*",)
    source_mapping: Optional[Mapping[str, str]] = None
    pbr: Optional[bool] = None
    pbr__files__packages_root: Optional[str] = None
    pbr__files__packages: Optional[str] = None
    provides_extra: Optional[Sequence[str]] = ()

    def _getHeaderAttrs(self) -> Sequence[Tuple[str, str, bool]]:
        # Until I invent a metadata version to include this, do so
        # unconditionally.
        # Stubs are wrong, this does too exist.
        return tuple(super()._getHeaderAttrs()) + (  # type: ignore[misc]
            ("X-Setup-Requires", "setup_requires", True),
            ("X-Tests-Require", "tests_require", True),
            ("???", "extras_require", False),
            ("X-Use-SCM-Version", "use_scm_version", False),
            ("x-Zip-Safe", "zip_safe", False),
            ("X-Test-Suite", "test_suite", False),
            ("X-Test-Loader", "test_loader", False),
            ("X-Include-Package-Data", "include_package_data", False),
            ("X-Namespace-Package", "namespace_packages", True),
            ("X-Package-Data", "package_data", False),
            ("X-Packages", "packages", True),
            ("X-Package-Dir", "package_dir", False),
            ("X-Packages-Dict", "packages_dict", False),
            ("X-Py-Modules", "py_modules", True),
            ("X-Entry-Points", "entry_points", False),
            ("X-Pbr", "pbr", False),
            ("X-pbr__files__packages_root", "pbr__files__packages_root", False),
            ("X-pbr__files__packages", "pbr__files__packages", True),
        )

    def asdict(self) -> Dict[str, Any]:
        d = {}
        for x in self:
            if getattr(self, x):
                d[x] = getattr(self, x)
        return d

    def _source_mapping(self, root: Path) -> Optional[Dict[str, str]]:
        """
        Returns install path -> src path

        If an exception like FileNotFound is encountered, returns None.
        """
        d: Dict[str, str] = {}

        for m in self.py_modules:
            if m == "?":
                return None
            m = m.replace(".", "/")
            d[f"{m}.py"] = f"{m}.py"

        try:
            # This commented block is approximately correct for setuptools, but
            # does not understand package_data.
            # # k = foo.bar, v = src/foo/bar
            # for k, v in self.packages_dict.items():
            #     kp = k.replace(".", "/")
            #     for item in (root / v).iterdir():
            #         if item.is_file():
            #             d[f"{kp}/{item.name}"] = f"{v}/{item.name}"

            # Instead, this behavior is more like flit/poetry by including all
            # files under package dirs, in a way that's mostly compatible with
            # setuptools setting package_dir dicts.  This tends to include
            # in-package tests, which is a behavior I like, but I'm sure some
            # people won't.

            seen_paths: Set[Path] = set()

            # Longest source path first, will "own" the item
            for k, v in sorted(
                self.packages_dict.items(), key=lambda x: len(x[1]), reverse=True
            ):
                kp = k.replace(".", "/")
                vp = root / v
                for item in vp.rglob("*"):
                    if item in seen_paths:
                        continue
                    seen_paths.add(item)
                    if item.is_file():
                        rel = item.relative_to(vp)
                        d[(kp / rel).as_posix()] = (v / rel).as_posix()

        except IOError:
            return None

        return d
