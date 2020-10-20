from pathlib import Path
from typing import Any, Dict

import imperfect

from ..types import Distribution
from .setup_and_metadata import SETUP_ARGS
from .types import SectionWriter


def from_setup_cfg(path: Path, markers: Dict[str, Any]) -> Distribution:

    cfg = imperfect.parse_string((path / "setup.cfg").read_text())

    d = Distribution()
    d.metadata_version = "2.1"

    for field in SETUP_ARGS:
        name = field.get_distribution_key()
        if not hasattr(d, name):
            continue

        cls = field.cfg.writer_cls
        if cls is SectionWriter:
            try:
                raw_section_data = cfg[field.cfg.section]
            except KeyError:
                continue
            # ConfigSection behaves like a Dict[str, str] so this is fine
            parsed = SectionWriter().from_ini_section(raw_section_data)  # type: ignore
        else:
            try:
                # All fields are defined as underscore, but it appears
                # setuptools normalizes so dashes are ok too.
                key = field.cfg.key
                if key not in cfg[field.cfg.section]:
                    key = key.replace("_", "-")
                raw_data = cfg[field.cfg.section][key]
            except KeyError:
                continue
            parsed = cls().from_ini(raw_data)

        setattr(d, name, parsed)
    return d
