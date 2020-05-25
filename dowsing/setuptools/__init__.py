from pathlib import Path

import imperfect

from ..types import BaseReader, Distribution
from .setup_cfg_parsing import from_setup_cfg
from .setup_py_parsing import from_setup_py


class SetuptoolsReader(BaseReader):
    def __init__(self, path: Path):
        self.path = path

    def get_requires_for_build_sdist(self):
        # TODO the documented behavior of pip (setuptools with a version
        # constraint) and what the pep517 module's build.compat_system does
        # differ.
        #
        # https://pip.pypa.io/en/stable/reference/pip/#pep-517-and-518-support
        # https://github.com/pypa/pep517/blob/master/pep517/build.py
        return ("setuptools",) + self._get_requires()

    def get_requires_for_build_wheel(self):
        return ("setuptools", "wheel") + self._get_requires()

    def get_metadata(self):
        if (self.path / "setup.cfg").exists():
            d1 = from_setup_cfg(self.path, {})
        else:
            d1 = Distribution()

        if (self.path / "setup.py").exists():
            d2 = from_setup_py(self.path, {})
            for k in d2:
                if getattr(d2, k):
                    setattr(d1, k, getattr(d2, k))

        return d1

    def _get_requires(self):
        dist = self.get_metadata()
        return tuple(dist.setup_requires)


if __name__ == "__main__":
    print(json.dumps(from_setup_cfg(Path(sys.argv[1]), {}).asdict(), indent=2))
