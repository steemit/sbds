SHELL := /bin/bash
ROOT_DIR := $(shell pwd)

DOCS_DIR := $(ROOT_DIR)/docs
DOCS_BUILD_DIR := $(DOCS_DIR)/_build

PROJECT_NAME := $(notdir $(ROOT_DIR))
PROJECT_DOCKER_TAG := steemit/$(PROJECT_NAME)

PYTHON := $(shell which python$(PYTHON_VERSION))
PIPENV_VENV_IN_PROJECT := 1
export PIPENV_VENV_IN_PROJECT
PYTHON_VERSION := 3.6
ENVFILE := .env

PROJECT_DOCKER_RUN_ARGS := -p8080:8080 --env-file .env

BUILD_DIR := $(ROOT_DIR)/build
OPERATIONS_CACHE_DIR=$(BUILD_DIR)
BLOCKCHAIN_EXAMPLES_DIR := $(OPERATIONS_CACHE_DIR)/examples

OPERATIONS_PREFIX := sbds/storages/db/tables/operations
OPERATIONS_PATH := $(ROOT_DIR)/$(OPERATION_PREFIX)
OPERATIONS_FILE := $(OPERATIONS_PATH)/operations_header.json
OPERATIONS_NAMES := $(shell jq -r '.classes[].name' $(OPERATIONS_FILE))
OPERATIONS_PYTHON_FILES := $(addprefix $(OPERATIONS_PATH)/, $(addsuffix .py, $(subst _operation,,$(OPERATIONS_NAMES))))

VIRTUAL_OPERATION_PREFIX := $(OPERATIONS_PREFIX)/virtual
VIRTUAL_OPERATIONS_PATH := $(ROOT_DIR)/$(VIRTUAL_OPERATION_PREFIX)
VIRTUAL_OPERATIONS_FILE := $(VIRTUAL_OPERATIONS_PATH)/virtual_operations_header.json
VIRTUAL_OPERATIONS_NAMES := $(shell jq -r '.classes[].name' $(VIRTUAL_OPERATIONS_FILE))
VIRTUAL_OPERATIONS_PYTHON_FILES := $(addprefix $(VIRTUAL_OPERATIONS_PATH)/, $(addsuffix .py, $(subst _operation,,$(VIRTUAL_OPERATIONS_NAMES))))


default: help

.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: init
init: clean ## install project requrements into .venv
	pip3 install --upgrade pipenv
	-pipenv --rm
	if [[ $(shell uname) == 'Darwin' ]]; then \
	brew install openssl; \
	env LDFLAGS="-L$(shell brew --prefix openssl)/lib" CFLAGS="-I$(shell brew --prefix openssl)/include" pipenv update --python $(PYTHON) --dev; \
	else \
		pipenv update --python $(PYTHON) --dev; \
	fi
	pipenv run pre-commit install

Pipfile.lock: Pipfile
	$(shell docker run $(PROJECT_DOCKER_TAG) /bin/bash -c 'pipenv lock && cat Pipfile.lock' > $@)

.PHONY: clean
clean: unmac ## clean python and dev junk
	find . -name "__pycache__" | xargs rm -rf
	-rm -rf .cache
	-rm -rf .eggs
	-rm -rf .mypy_cache
	-rm -rf *.egg-info
	-rm -rf *.log
	-rm -rf service/*/supervise

.PHONY: build
build: clean clean-perf ## build docker image
	docker build -t $(PROJECT_DOCKER_TAG) .

.PHONY: run
run: ## run docker image
	docker run $(PROJECT_DOCKER_RUN_ARGS) $(PROJECT_DOCKER_TAG)

.PHONY: run-local
run-local: ## run the python app without docker
	pipenv run python3 -m jussi.serve  --debug=1 --server_workers=1 --upstream_config_file ALT_CONFIG.json

.PHONY: test
test: ## run all tests
	pipenv run pytest

.PHONY: test-with-docker
test-with-docker: Pipfile.lock build  ## run tests that depend on docker
	pipenv run pytest --rundocker --jussiurl http://localhost:8080

.PHONY: lint
lint: ## lint python files
	pipenv run pylint $(PROJECT_NAME)

.PHONY: fmt
fmt: ## format python files
    # yapf is disabled until the update 3.6 fstring compat
	pipenv run yapf --in-place --style pep8 --recursive $(PROJECT_NAME) tests
	pipenv run autopep8 --verbose --verbose --max-line-length=100 --aggressive --jobs -1 --in-place  --recursive $(PROJECT_NAME) tests

.PHONY: fix-imports
fix-imports: remove-unused-imports sort-imports ## remove unused and then sort imports

.PHONY: remove-unused-imports
remove-unused-imports: ## remove unused imports from python files
	pipenv run autoflake --in-place --remove-all-unused-imports --recursive $(PROJECT_NAME) tests

.PHONY: sort-imports
sort-imports: ## sorts python imports using isort with settings from .editorconfig
	pipenv run isort --verbose --recursive --atomic --settings-path  .editorconfig --virtual-env .venv $(PROJECT_NAME) tests

.PHONY: pipenv-check
pipenv-check:
	pipenv check

.PHONY: pre-commit
pre-commit: ## run pre-commit against modified files
	pipenv run pre-commit run

.PHONY: pre-commit-all
pre-commit-all: ## run pre-commit against all files
	pipenv run pre-commit run --all-files

.PHONY: unmac
unmac:
	find $(ROOT_DIR) -type f -name '.DS_Store' -delete

.PHONY: prepare
prepare: fix-imports lint fmt pre-commit-all pipenv-check test unmac  ## fix-imports lint fmt pre-commit-all pipenv-check test

.PHONY: prepare-and-build
prepare-and-build: prepare Pipfile.lock build  ## run all tests, formatting and pre-commit checks, then build docker image

.PHONY: prepare-and-test
prepare-and-test: prepare test-with-docker ## run all tests, formatting and pre-commit checks, build docker image, test docker image

.PHONY: sql
sql:
	 MYSQL_HOME=$(ROOT_DIR) mysql

.PHONY: ipython
ipython:
	envdir envd pipenv run ipython -i sbds/storages/db/scripts/ipython_init.py

README.rst: docs/src/README.rst 
	cd $(DOCS_DIR) && $(MAKE) README

$(BUILD_DIR):
	mkdir $@

$(BLOCKCHAIN_EXAMPLES_DIR): $(BUILD_DIR)
	mkdir $@

$(BLOCKCHAIN_EXAMPLES_DIR)/%.json: $(BLOCKCHAIN_EXAMPLES_DIR)
	pipenv run ./contrib/codegen.py generate-class-example $(*F) $(DATABASE_URL) > $@

$(VIRTUAL_OPERATIONS_PATH)/%.py: $(VIRTUAL_OPERATIONS_FILE)
	pipenv run ./contrib/codegen.py generate-class $(*F) \
		$(VIRTUAL_OPERATIONS_FILE) \
		--cache_dir $(OPERATIONS_CACHE_DIR) \
		--db_url $(DATABASE_URL) > $@

$(OPERATIONS_PATH)/%.py: $(OPERATIONS_FILE)
	pipenv run ./contrib/codegen.py generate-class $(*F) \
		$(OPERATIONS_FILE) \
		--cache_dir $(OPERATIONS_CACHE_DIR) \
		--db_url $(DATABASE_URL) > $@

.PHONY: virtual-ops-classes
virtual-ops-classes: $(VIRTUAL_OPERATIONS_PYTHON_FILES)
