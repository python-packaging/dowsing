PYTHON?=python3
SOURCES=dowsing setup.py

.PHONY: venv
venv:
	$(PYTHON) -m venv .venv
	source .venv/bin/activate && make setup
	@echo 'run `source .venv/bin/activate` to use virtualenv'

# The rest of these are intended to be run within the venv, where python points
# to whatever was used to set up the venv.

.PHONY: setup
setup:
	python -m pip install -Ue .[dev,test]

.PHONY: test
test:
	python -m coverage run -m dowsing.tests $(TESTOPTS)
	python -m coverage report

.PHONY: format
format:
	python -m ufmt format $(SOURCES)

.PHONY: lint
lint:
	python -m ufmt check $(SOURCES)
	python -m flake8 $(SOURCES)
	mypy --strict dowsing

.PHONY: release
release:
	rm -rf dist
	python setup.py sdist bdist_wheel
	twine upload dist/*
