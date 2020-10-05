from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, Union


# These implement the basic types listed at
# https://setuptools.readthedocs.io/en/latest/setuptools.html#specifying-values
class BaseWriter:
    def to_ini(self, value: Any) -> str:  # pragma: no cover
        raise NotImplementedError

    def from_ini(self, value: str) -> Any:  # pragma: no cover
        raise NotImplementedError


class StrWriter(BaseWriter):
    def to_ini(self, value: str) -> str:
        return value

    def from_ini(self, value: str) -> str:
        return value


class ListCommaWriter(BaseWriter):
    def to_ini(self, value: List[str]) -> str:
        if not value:
            return ""
        return "".join(f"\n  {k}" for k in value)

    def from_ini(self, value: str) -> List[str]:
        # TODO, on all of these, handle other separators, \r, and stripping
        return [line.strip() for line in value.strip().split("\n")]


class ListCommaWriterCompat(BaseWriter):
    def to_ini(self, value: Union[str, List[str]]) -> str:
        if not value:
            return ""
        if isinstance(value, str):
            value = [value]
        return "".join(f"\n  {k}" for k in value)

    def from_ini(self, value: str) -> List[str]:
        return [line.strip() for line in value.strip().split("\n")]


class ListSemiWriter(BaseWriter):
    def to_ini(self, value: List[str]) -> str:
        if not value:
            return ""
        return "".join(f"\n  {k}" for k in value)

    def from_ini(self, value: str) -> List[str]:
        return [line.strip() for line in value.strip().split("\n")]


# This class is also specialcased
class SectionWriter(BaseWriter):
    def to_ini(self, value: List[str]) -> str:
        if not value:
            return ""
        return "".join(f"\n{k}" for k in value)

    def from_ini_section(self, section: Dict[str, str]) -> Dict[str, List[str]]:
        return {k: section[k].strip().split("\n") for k in section.keys()}


class BoolWriter(BaseWriter):
    def to_ini(self, value: bool) -> str:
        return "true" if value else "false"

    def from_ini(self, value: str) -> bool:
        # TODO
        return value.lower() == "true"


class DictWriter(BaseWriter):
    def to_ini(self, value: Dict[str, str]) -> str:
        if not value:
            return ""
        return "".join(f"\n  {k}={v}" for k, v in value.items())

    def from_ini(self, value: str) -> Dict[str, str]:
        d = {}
        for line in value.strip().split("\n"):
            a, b, c = line.partition("=")
            a = a.strip()
            c = c.strip()
            d[a] = c
        return d


@dataclass
class SetupCfg:
    section: str
    key: str
    writer_cls: Type[BaseWriter] = StrWriter


@dataclass
class PyProject:
    section: str
    key: str
    # TODO setuptools-only?


@dataclass
class Metadata:
    key: str
    repeated: bool = False


@dataclass
class ConfigField:
    """
    A ConfigField is almost a 1:1 mapping to metadata fields.

    The writer_cls in SetupCfg should translate between the richer value used in
    Python, and the serialized-in-ini value, including complex things like
    indents.
    """

    # The kwarg to setup()
    keyword: str
    # The section/key in setup.cfg
    cfg: SetupCfg
    # TODO PyProject reference
    # The key in METADATA files
    metadata: Optional[Metadata] = None
    # Used for automatic test generation; use None if it should be skipped.
    sample_value: Optional[Any] = "foo"
    # Not all kwargs end up in metadata.  We have a modified Distribution that
    # keeps them for now, but looking for something better (even if it's just
    # using ConfigField objects as events in a stream).
    distribution_key: Optional[str] = None

    def get_distribution_key(self) -> str:
        # Returns the member name of pkginfo.Distribution (or our subclasS)
        if self.metadata is not None:
            return (
                (self.distribution_key or self.metadata.key or self.keyword)
                .replace("-", "_")
                .lower()
            )
        else:
            return (self.distribution_key or self.keyword).replace("-", "_").lower()
