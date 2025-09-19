# Makefile for YoClip

.PHONY: help install install-dev test lint format type-check clean build upload

help:
	@echo "Available commands:"
	@echo "  install      Install the package"
	@echo "  install-dev  Install in development mode with dev dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run linting"
	@echo "  format       Format code"
	@echo "  type-check   Run type checking"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build the package"
	@echo "  upload       Upload to PyPI"

install:
	pip install .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

lint:
	flake8 yoclip tests

format:
	black yoclip tests
	isort yoclip tests

type-check:
	mypy yoclip

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete

build:
	python -m build

upload:
	python -m twine upload dist/*
