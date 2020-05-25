from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass
class EnvironmentMarkers:
    """
    An 80% correct implementation of PEPs 496 and 508.

    This class is an implementation detail, and subject to change to make it
    more correct later.  If you just want to match a certain version of cpython
    on linux, you should use `linux_env(version="1.2.3")` which happens to
    return an instance of this.
    """

    python_version: str  # TODO: ought to be a Version, or at least validate the num dots.
    os_name: str = "posix"
    sys_platform: str = "linux"
    platform_machine: str = "x86_64"
    platform_python_implementation: str = "CPython"
    platform_system: str = "Linux"
    implementation_name: str = "cpython"

    # I've not seen these in the wild; we leave them as None currently
    platform_release: Optional[str] = None  # `uname -r`
    platform_version: Optional[str] = None  # `uname -v`
    python_full_version: Optional[str] = None

    # The `extra` field is not really documented; PEP 508 makes brief mention of
    # there being "no current specification for this."  It appears that
    # setuptools, when outputting requires.txt, transforms `extras_require` into
    # something that looks like a marker test string, but it checks, with `==`,
    # a string a the extras set.  If they'd use `in` as the operator, it would
    # go against PEP 345, so we have to wrap the set with `Extras` before
    # evaluating.
    #
    # This field is never used in this class, but only included for
    # completeness.
    extra: Optional[str] = None

    def __post_init__(self) -> None:
        if self.sys_platform == "linux":
            if self.python_version and self.python_version[:1] == "2":
                self.sys_platform = "linux2"
        elif self.sys_platform == "win32":
            self.platform_system = "Windows"
            self.os_name = "nt"
        elif self.sys_platform == "darwin":
            self.platform_system = "Darwin"
        else:
            raise TypeError(f"Unknown sys_platform: {self.sys_platform!r}")


def linux_env(python_version: str) -> EnvironmentMarkers:
    # TODO support full_version, e.g. beta releases
    return EnvironmentMarkers(python_version=python_version)


class Extras:
    """
    This is a tiny class that lets us get 'extra == "foo"' working for
    `packaging.markers`
    """

    def __init__(self, extras: Iterable[str]) -> None:
        self.extras = extras

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, str):
            return False
        return other in self.extras
