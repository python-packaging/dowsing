from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, Union


# These implement the basic types listed at
# https://setuptools.readthedocs.io/en/latest/setuptools.html#specifying-values
class BaseWriter:
    def to_ini(self, value: Any) -> str:  # pragma: no cover
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
        return "".join(f"\n{k}" for k in value)

    def from_ini(self, value: str) -> List[str]:
        # TODO, on all of these, handle other separators, \r, and stripping
        return value.split("\n")


class ListCommaWriterCompat(BaseWriter):
    def to_ini(self, value: Union[str, List[str]]) -> str:
        if not value:
            return ""
        if isinstance(value, str):
            value = [value]
        return "".join(f"\n{k}" for k in value)

    def from_ini(self, value: str) -> List[str]:
        return value.split("\n")


class ListSemiWriter(BaseWriter):
    def to_ini(self, value: List[str]) -> str:
        if not value:
            return ""
        return "".join(f"\n{k}" for k in value)

    def from_ini(self, value: str) -> List[str]:
        return value.split("\n")


# This class is also specialcased
class SectionWriter(BaseWriter):
    def to_ini(self, value: List[str]) -> str:
        if not value:
            return ""
        return "".join(f"\n{k}" for k in value)


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
        return "".join(f"\n{k}={v}" for k, v in value.items())

    def from_ini(self, value: str) -> Dict[str, str]:
        d = {}
        for line in value.split("\n"):
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

    The writers in SetupCfg should translate between the richer value used in 
    """

    # The kwarg to setup()
    keyword: str
    cfg: SetupCfg
    metadata: Optional[Metadata] = None
    sample_value: Optional[Any] = "foo"
    # Not all kwargs end up in metadata.  We have a modified Distribution that
    # keeps them for now, but looking for something better (even if it's just
    # using ConfigField objects as events in a stream).
