.PHONY: start install precommit test clean

VENV=.venv_311
PIP=$(VENV)/bin/pip
PYTHON=$(VENV)/bin/python
PRECOMMIT=$(VENV)/bin/pre-commit
PYTEST=$(VENV)/bin/pytest

start:
	@echo "Pour activer l'environnement virtuel sous Windows CMD :"
	@echo "$(VENV)\\Scripts\\activate.bat"

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements-dev.txt
	python -m pip install pre-commit

precommit:
	pre-commit install

test:
	pytest --maxfail=1 --disable-warnings -v

clean:
	find . -name '*.pyc' -delete
