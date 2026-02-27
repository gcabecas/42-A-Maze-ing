PYTHON = python3
MAIN = a_maze_ing.py
CONFIG ?= config.txt

.PHONY: venv install run debug clean lint lint-strict

run:
    .venv/bin/activate; $(PYTHON) $(MAIN) $(CONFIG)

venv:
    $(PYTHON) -m venv .venv

install:
    .venv/bin/activate; $(PYTHON) -m pip install -r requirement.txt

debug:
    .venv/bin/activate; $(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
    rm -rf __pycache__ .mypy_cache

lint:
    .venv/bin/activate; flake8 --exclude .venv
    .venv/bin/activate; mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
    flake8 --exclude .venv .
    mypy . --strict