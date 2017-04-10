SHELL := /bin/bash
ROOT_DIR := $(shell pwd)
DOCS_DIR := $(ROOT_DIR)/docs
DOCS_BUILD_DIR := $(DOCS_DIR)/_build


default: build

.PHONY: test run test-without-lint test-pylint fmt test-without-build build test-in-venv init

init:
	pip install pipenv
	pipenv lock
	pipenv install --three --dev

build:
	docker build -t steemit/sbds .

run:
	docker run steemit/sbds

test:
	pipenv run py.test tests

lint:
	 pipenv run py.test --pylint -m pylint sbds

fmt:
	pipenv run yapf --recursive --in-place --style pep8 sbds
	pipenv run autopep8 --recursive --in-place sbds

README.rst: docs/src/README.rst 
	cd $(DOCS_DIR) && $(MAKE) README
