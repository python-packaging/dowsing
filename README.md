# dowsing

TODO: Reword so it flows better.

## Basic reasoning

The reality of python packaging, even with recent PEPs, is that most nontrivial
python packages do moderately interesting stuff in their `setup.py`:

* Imports (either from local code, or `setup_requires`)
* Fetching things from the Internet
* Running commands
* Making sure native libs are installed, or there's a working C compiler
* Choosing deps based on platform

The disappointing part of several of these from the perspective of basically
running a distro, is that they produce messages intended for humans, rather than
actually using the mechanisms that we have in PEP 508 (environment markers) and
518 (pyproject.toml requires).

## Goals

This project is a bridge to find several things out, about primarily setup.py
but also understanding PEP 517/518 as a one-stop-shop, about:

* for cases where the package's version is stored within, but has external
  requirements that are not listed at build-time, currently returns an unknown
  value and moves on
* potential imports, to guess at what should have been in the build-time
  requirements (e.g `numpy.distutils` is pretty clear)
* doesn't actually execute, so fetches or execs can't cause it to fail
* Gives the PEP 517 APIs `get_requirements_for_sdist` and
  `get_requirements_for_build_wheel`, even on a different platform through
  simulated execution, with no sandboxing required.
* A lower-level api suitable for making edits to the place where the setup args
  are defined.

## Doing this "right"

A bunch of this is papering over problems with the current reality.  If you have
an existing sandbox and are ok with ~30% of projects just failing to build, you
can rely on the `pep517` module's API to actually execute the code on the
current version of python.

If you're willing to run the code and have it take longer, take a look at the
pep517 api `get_requires_for_*` or have it generate the metadata (assuming
what you want is in there).  An example is in `dowsing/_demo_pep517.py`

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
