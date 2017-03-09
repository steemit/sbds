SHELL := /bin/bash
ROOT_DIR := $(shell pwd)
DOCS_DIR := $(ROOT_DIR)/docs
DOCS_BUILD_DIR := $(DOCS_DIR)/_build


default: build

.PHONY: test run test-without-lint test-pylint fmt test-without-build build test-in-venv

build:
	docker build -t steemit/sbds .

run:
	docker run steemit/sbds

test: test-without-build build

test-without-build: test-without-lint test-pylint

test-without-lint:
	py.test tests

test-pylint:
	py.test --pylint -m pylint sbds

fmt:
	yapf --recursive --in-place --style pep8 sbds
	autopep8 --recursive --in-place .

README.rst: docs/src/README.rst 
	cd $(DOCS_DIR) && $(MAKE) README
