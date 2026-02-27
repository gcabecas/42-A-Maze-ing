PYTHON = python3
MAIN = a_maze_ing.py
CONFIG ?= config.txt

.PHONY: venv install run debug clean lint lint-strict

venv:
	$(PYTHON) -m venv .venv
	@echo "Venv created. Activate it with: source .venv/bin/activate"
install:
	$(PYTHON) -m pip install -r requirement.txt

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf __pycache__ .mypy_cache

lint:
	flake8 --exclude .venv
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 --exclude .venv .
	mypy . --strict
