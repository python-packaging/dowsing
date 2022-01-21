import tomlkit
from setuptools import find_packages

from .types import BaseReader, Distribution


class Pep621Reader(BaseReader):
    def get_pep621_metadata(self) -> Distribution:
        pyproject = self.path / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())

        d = Distribution()
        d.metadata_version = "2.1"
        d.project_urls = {}
        d.entry_points = {}
        d.requires_dist = []
        d.packages = []
        d.packages_dict = {}

        table = doc.get("project", None)
        if table:
            for k, v in table.items():
                if k == "name":
                    if (self.path / f"{v}.py").exists():
                        d.py_modules = [v]
                    else:
                        d.packages = find_packages(
                            self.path.as_posix(), include=(f"{v}.*")
                        )
                        d.packages_dict = {i: i.replace(".", "/") for i in d.packages}
                elif k == "license":
                    if "text" in v:
                        v = v["text"]
                    elif "file" in v:
                        v = f"file: {v['file']}"
                    else:
                        raise ValueError("no known license field values")
                elif k == "dependencies":
                    k = "requires_dist"
                elif k == "optional-dependencies":
                    pass
                elif k == "urls":
                    d.project_urls.update(v)

                k2 = k.replace("-", "_")
                if k2 in d:
                    setattr(d, k2, v)

        return d
