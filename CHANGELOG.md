## v0.9.0b3

* Support PEP 639 style metadata (#76)
* Support more `setup.py` assignments (#57)
* 3.12 compat (depends on setuptools)
* Fix tests to work on modern Python

## v0.9.0b2

* `source_mapping` bugfixes
  * `packages` being an empty string (#20)
  * `py_modules` containing dots (#22)
  * Flit modules instead of packages (#24)
  * `setup.py` parsing addition operator (#25)

## v0.9.0b1

* Includes package data in `source_mapping` all the time.
* Support `flit.buildapi` as alternate flit build-backend
* Switch to usort for import sorting

## v0.8.0

* Adds `Distribution.source_mapping`
* Enable gh actions on 3.9

## v0.7.0

* Adds Poetry support
* Addd Maturin support
* Adds `packages_dict` and better `packages` support across supported backends
* Allows `setup.cfg` fields to use dashes

## v0.6.0

* Fix many bugs in Flit and Setuptools support, better test coverage.

## v0.5.0

* Initial code extracted from Opine
