"""
For testing, dump the requirements that we find using the pep517 project.
"""

import json
import sys

from pep517.build import compat_system
from pep517.envbuild import BuildEnvironment, Pep517HookCaller


def main(path: str) -> None:
    system = compat_system(path)
    hooks = Pep517HookCaller(path, system["build-backend"], system.get("backend-path"))

    # compat_system sets this to setuptools, wheel, even if the backend isn't
    # setuptools tho
    requires = system["requires"]

    d = {}
    with BuildEnvironment() as env:
        env.pip_install(requires)
        d["get_requires_for_build_sdist"] = (
            requires + hooks.get_requires_for_build_sdist(None)
        )
        d["get_requires_for_build_wheel"] = (
            requires + hooks.get_requires_for_build_wheel(None)
        )

    print(json.dumps(d))


if __name__ == "__main__":
    main(sys.argv[1])
