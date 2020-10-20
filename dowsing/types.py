from pathlib import Path
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


# TODO: pkginfo isn't typed, and is doing to require a yak-shave to send a PR
# since it's on launchpad.
class Distribution(pkginfo.distribution.Distribution):  # type: ignore
    # These are not actually part of the metadata, see PEP 566
    setup_requires: Sequence[str] = ()
    tests_require: Sequence[str] = ()
    extras_require: Dict[str, Sequence[str]] = {}
    use_scm_version: Optional[bool] = None
    zip_safe: Optional[bool] = None
    include_package_data: Optional[bool] = None
    test_suite: str = ""
    test_loader: str = ""
    namespace_packages: Sequence[str] = ()
    package_data: Dict[str, Sequence[str]] = {}
    packages: Sequence[str] = ()
    package_dir: Mapping[str, str] = {}
    packages_dict: Mapping[str, str] = {}
    entry_points: Dict[str, Sequence[str]] = {}
    find_packages_where: str = "."
    find_packages_exclude: Sequence[str] = ()
    find_packages_include: Sequence[str] = ("*",)

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
            ("X-Entry-Points", "entry_points", False),
        )

    def asdict(self) -> Dict[str, Any]:
        d = {}
        for x in self:
            if getattr(self, x):
                d[x] = getattr(self, x)
        return d
