PYTHON = .venv/bin/python
MAIN = a_maze_ing.py
CONFIG ?= config.txt

.PHONY: venv install run debug clean lint lint-strict package

run:
	$(PYTHON) $(MAIN) $(CONFIG)

venv:
	python3 -m venv .venv

install:
	$(PYTHON) -m pip install -r requirement.txt

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf __pycache__ .mypy_cache mazegen/__pycache__

lint:
	.venv/bin/flake8 --exclude .venv
	.venv/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	.venv/bin/flake8 --exclude .venv .
	.venv/bin/mypy . --strict

build:
	$(PYTHON) -m pip install --upgrade build setuptools wheel
	$(PYTHON) -m build