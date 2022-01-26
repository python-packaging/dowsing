import sys
from pathlib import Path
from typing import List

import click
from honesty.archive import extract_and_get_names
from honesty.cache import Cache
from honesty.cmdline import select_versions, wrap_async
from honesty.releases import async_parse_index, FileType
from moreorless.click import echo_color_unified_diff

from dowsing.pep517 import get_metadata


@click.command()
@click.argument("packages", nargs=-1)
@wrap_async
async def main(packages: List[str]) -> None:
    # Much of this code mirrors the methods in honesty/cmdline.py
    async with Cache(fresh_index=True) as cache:
        for package_name in packages:
            package_name, operator, version = package_name.partition("==")
            try:
                package = await async_parse_index(package_name, cache, use_json=True)
            except Exception as e:
                print(package_name, repr(e), file=sys.stderr)
                continue

            selected_versions = select_versions(package, operator, version)
            rel = package.releases[selected_versions[0]]

            sdists = [f for f in rel.files if f.file_type == FileType.SDIST]
            wheels = [f for f in rel.files if f.file_type == FileType.BDIST_WHEEL]

            if not sdists or not wheels:
                print(f"{package_name}: insufficient artifacts")
                continue

            sdist_path = await cache.async_fetch(pkg=package_name, url=sdists[0].url)
            wheel_path = await cache.async_fetch(pkg=package_name, url=wheels[0].url)

            sdist_root, sdist_filenames = extract_and_get_names(
                sdist_path, strip_top_level=True, patterns=("*.*")
            )
            wheel_root, wheel_filenames = extract_and_get_names(
                wheel_path, strip_top_level=True, patterns=("*.*")
            )

            try:
                subdirs = tuple(Path(sdist_root).iterdir())
                metadata = get_metadata(Path(sdist_root, subdirs[0]))
                assert metadata.source_mapping is not None, "no source_mapping"
            except Exception as e:
                print(package_name, repr(e), file=sys.stderr)
                continue

            skip_patterns = [
                ".so",
                ".pyc",
                "nspkg",
                ".dist-info",
                ".data/scripts",
            ]
            wheel_blob = "".join(
                sorted(
                    f"{f[0]}\n"
                    for f in wheel_filenames
                    if not any(s in f[0] for s in skip_patterns)
                )
            )
            md_blob = "".join(sorted(f"{f}\n" for f in metadata.source_mapping.keys()))

            if metadata.source_mapping == {}:
                print(f"{package_name}: empty dict")
            elif md_blob == wheel_blob:
                print(f"{package_name}: ok")
            elif md_blob in ("", "?.py\n"):
                print(f"{package_name}: COMPLETELY MISSING")
            else:
                echo_color_unified_diff(
                    wheel_blob, md_blob, f"{package_name}/files.txt"
                )


if __name__ == "__main__":
    main()
