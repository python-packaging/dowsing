# dowsing

Short version:

```
python -m dowsing.pep517 /path/to/repo | jq .
```

or

```
from dowsing.pep517 import get_metadata
dist = get_metadata(Path("/path/to/repo"))
```

## Basic reasoning

I don't want to execute arbitrary `setup.py` in order to find out their basic
metadata.  I don't want to use the pep517 module in a sandbox, because commonly
packages forget to list their build-time dependencies.

This project is one step better than grepping source files, but also understands
`build-system` in `pyproject.toml` (from PEP 517/518).  It does pretty well run
on a sampling of pypi projects, but does fail on some notable ones (including
setuptools).

When it fails, a key will be `"??"` and due to some quirks in list context, this
can be `["?", "?"]`.

## A rant

The reality of python packaging, even with recent PEPs, is that most nontrivial
python packages do moderately interesting stuff in their `setup.py`:

* Imports (either from local code, or `setup_requires`)
* Fetching things from the Internet
* Running commands
* Making sure native libs are installed, or there's a working C compiler
* Choosing deps based on platform

From the perspective of basically running a distro, they produce messages
intended for humans, rather than actually using the mechanisms that we have in
PEP 508 (environment markers) and 518 (pyproject.toml requires).  There is also
no well-specified way to request native libs, and many projects choose to fail
to run `setup.py` when libs are missing.

## Goals

This project is a bridge to find several things out, about primarily setup.py
but also understanding some popular PEP 517/518 builders as a one-stop-shop, about:

* doesn't actually execute, so fetches or execs can't cause it to fail [done]
* cases where we could find out the version string, but it fails to import [done]
* lets you simulate the `pep517` module's output on different platforms [done]
* a lower-level api suitable for making edits to the place where the setup args
  are defined [done]
* to list potential imports, and guess at missing build-time deps (something
  like `numpy.distutils` is pretty clear) [todo]

## Doing this "right"

A bunch of this is papering over problems with the current reality.  If you have
an existing sandbox and are ok with ~30% of projects just failing to build, you
can rely on the `pep517` module's API to actually execute the code on the
current version of python.

If you're willing to run the code and have it take longer, take a look at the
pep517 api `get_requires_for_*` or have it generate the metadata (assuming
what you want is in there).  An example is in `dowsing/_demo_pep517.py`

This project's `dowsing.pep517` api is designed to do something similar, but not
fail on missing build-time requirements.


# Further Reading

* PEP 241, Metadata 1.0
* PEP 314, Metadata 1.1
* PEP 345, Metadata 1.2
* PEP 566, Metadata 2.1
* https://packaging.python.org/specifications/core-metadata/
* https://setuptools.readthedocs.io/en/latest/setuptools.html#metadata

# License

dowsing is copyright [Tim Hatch](http://timhatch.com/), and licensed under
the MIT license.  I am providing code in this repository to you under an open
source license.  This is my personal repository; the license you receive to
my code is from me and not from my employer. See the `LICENSE` file for details.
