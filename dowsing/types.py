from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

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
    namespace_packages: Sequence[str] = ()

    def _getHeaderAttrs(self) -> Sequence[Tuple[str, str, bool]]:
        # Until I invent a metadata version to include this, do so
        # unconditionally.
        return tuple(super()._getHeaderAttrs()) + (
            ("Setup-Requires", "setup_requires", True),
            ("Tests-Require", "tests_require", True),
            ("???", "extras_require", False),
            ("Use-SCM-Version", "use_scm_version", False),
            ("Zip-Safe", "zip_safe", False),
            ("Test-Suite", "test_suite", False),
            ("Include-Package-Data", "include_package_data", False),
            ("Namespace-Package", "namespace_packages", True),
        )

    def asdict(self) -> Dict[str, Any]:
        d = {}
        for x in self:
            if getattr(self, x):
                d[x] = getattr(self, x)
        return d
