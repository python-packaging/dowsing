from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

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

# TODO: pkginfo isn't typed, and is doing to require a yak-shave to send a PR
# since it's on launchpad.
class Distribution(pkginfo.distribution.Distribution):  # type: ignore
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

    def _getHeaderAttrs(self) -> Sequence[Tuple[str, str, bool]]:
        # Until I invent a metadata version to include this, do so
        # unconditionally.
        return tuple(super()._getHeaderAttrs()) + (
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
            d[f"{m}.py"] = f"{m}.py"

        try:
            # k = foo.bar, v = src/foo/bar
            for k, v in self.packages_dict.items():
                kp = k.replace(".", "/")
                for item in (root / v).iterdir():
                    if item.is_file():
                        d[f"{kp}/{item.name}"] = f"{v}/{item.name}"
        except IOError:
            return None

        return d
