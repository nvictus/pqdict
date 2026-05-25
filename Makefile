.PHONY: install lint fmt test typecheck typecheck-ty docs build clean publish

install:
	uv sync

lint:
	uv run ruff check

fmt:
	uv run ruff format

test:
	uv run pytest

typecheck-mypy:
	uv run mypy pqdict

typecheck-pyright:
	uv run pyright pqdict

typecheck-ty:
	uv run ty check pqdict tests

docs:
	uv run --group docs sphinx-autobuild docs docs/_build/html

build: clean
	uv build

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

publish: 
	uv run --with twine twine upload dist/*
