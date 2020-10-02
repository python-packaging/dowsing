from pathlib import Path
from typing import Any, Dict

import imperfect

from ..types import Distribution
from .setup_and_metadata import SETUP_ARGS


def from_setup_cfg(path: Path, markers: Dict[str, Any]) -> Distribution:

    cfg = imperfect.parse_string((path / "setup.cfg").read_text())

    d = Distribution()
    d.metadata_version = "2.1"

    for field in SETUP_ARGS:
        # Until there's a better representation...
        if not field.metadata and field.keyword not in ("setup_requires",):
            continue

        try:
            raw_data = cfg[field.cfg.section][field.cfg.key]
        except KeyError:
            continue
        cls = field.cfg.writer_cls
        parsed = cls().from_ini(raw_data)

        name = (
            (field.metadata.key if field.metadata else field.keyword)
            .lower()
            .replace("-", "_")
        )
        setattr(d, name, parsed)
    return d
