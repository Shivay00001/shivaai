# Makefile for ShivAI
# Common development commands

.PHONY: help install dev test lint format clean build run docs

# Default target
help:
	@echo "ShivAI Development Commands:"
	@echo ""
	@echo "  make install       Install package and dependencies"
	@echo "  make dev           Install with dev dependencies"
	@echo "  make test          Run tests with pytest"
	@echo "  make lint          Run linters (ruff, mypy)"
	@echo "  make format        Format code with black and ruff"
	@echo "  make clean         Clean build artifacts"
	@echo "  make build         Build Python wheel"
	@echo "  make run           Run ShivAI agent"
	@echo "  make run-text      Run in text-only mode"
	@echo "  make docs          Build documentation"
	@echo "  make models        Download Vosk speech models"
	@echo ""

# Installation
install:
	pip install -e .

dev:
	pip install -e ".[dev,test]"
	pre-commit install

# Testing
test:
	pytest tests/ -v --cov=shivai --cov-report=term-missing

test-fast:
	pytest tests/ -v -m "not slow"

test-integration:
	pytest tests/ -v -m integration

test-coverage:
	pytest tests/ --cov=shivai --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

# Code quality
lint:
	ruff check shivai/ tests/
	mypy shivai/

format:
	black shivai/ tests/
	ruff check --fix shivai/ tests/

format-check:
	black --check shivai/ tests/
	ruff check shivai/ tests/

# Cleaning
clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .coverage htmlcov/
	rm -rf .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Building
build: clean
	python -m build

build-wheel:
	python -m build --wheel

# Running
run:
	python -m shivai

run-text:
	python -m shivai --text

run-debug:
	python -m shivai --debug

# Documentation
docs:
	cd docs && mkdocs build
	@echo "Documentation: docs/site/index.html"

docs-serve:
	cd docs && mkdocs serve

# Models
models:
	./scripts/setup-vosk-models.sh

# Desktop build
build-desktop:
	cd desktop && npm install && npm run build

# Mobile build
build-apk:
	cd mobile && flutter build apk --release

# Web build
build-web:
	cd web && npm install && npm run build

# All builds
build-all: build build-desktop build-apk build-web
	@echo "All artifacts built successfully!"

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Pre-commit
pre-commit:
	pre-commit run --all-files

# Release
release-patch:
	bumpversion patch

release-minor:
	bumpversion minor

release-major:
	bumpversion major
