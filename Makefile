.PHONY: install test clean build publish

install:
	pip install -e .

test:
	pytest

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/

build: clean
	python setup.py sdist
	python setup.py bdist_wheel

publish: 
	twine upload dist/*
