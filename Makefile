SHELL := /bin/bash
ROOT_DIR := $(shell pwd)

DOCS_DIR := $(ROOT_DIR)/docs
DOCS_BUILD_DIR := $(DOCS_DIR)/_build

PROJECT_NAME := $(notdir $(ROOT_DIR))
PROJECT_DOCKER_TAG := steemit/$(PROJECT_NAME)

PYTHON_VERSION := 3.6
PYTHON := $(shell which python$(PYTHON_VERSION))
PIPENV := $(shell which pipenv)
PIPENV_VENV_IN_PROJECT := 1
export PIPENV_VENV_IN_PROJECT

ENVFILE := .env

PROJECT_DOCKER_RUN_ARGS := -p8080:8080 --env-file .env

BUILD_DIR := $(ROOT_DIR)/build

CODEGEN_PATH := sbds/codegen
EXAMPLES_PATH :=$(CODEGEN_PATH)/examples
HEADERS_PATH := $(CODEGEN_PATH)/headers
TEMPLATES_PATH := $(CODEGEN_PATH)/templates

SBDS_BASE_CMD := $(PIPENV) run python -m sbds.cli

STORAGES_DB_PATH := sbds/storages/db
VIEWS_PATH := $(STORAGES_DB_PATH)/views
TABLES_PATH := $(STORAGES_DB_PATH)/tables
META_PATH := $(TABLES_PATH)/meta
OPERATIONS_PATH := $(TABLES_PATH)/operations
VIRTUAL_OPERATIONS_PATH := $(TABLES_PATH)/operations/virtual

OPERATIONS_HEADER_FILE := $(HEADERS_PATH)/operations_header.json
VIRTUAL_OPERATIONS_HEADER_FILE := $(HEADERS_PATH)/virtual_operations_header.json

OPERATION_NAMES := $(filter %operation, $(shell jq -r '.classes[].name' $(OPERATIONS_HEADER_FILE)))
VIRTUAL_OPERATION_NAMES := $(filter %operation, $(shell jq -r '.classes[].name' $(VIRTUAL_OPERATIONS_HEADER_FILE)))

OPERATION_PYTHON_FILES := $(addprefix $(OPERATIONS_PATH)/, $(addsuffix .py, $(subst _operation,,$(OPERATION_NAMES))))
VIRTUAL_OPERATION_PYTHON_FILES := $(addprefix $(VIRTUAL_OPERATIONS_PATH)/, $(addsuffix .py, $(subst _operation,,$(VIRTUAL_OPERATION_NAMES))))

META_NAMES := accounts
META_PYTHON_FILES := $(addprefix $(VIEWS_PATH)/, $(addsuffix .py, $(META_NAMES)))

VIEWS_NAMES := accounts accounts_history
VIEWS_PYTHON_FILES := $(addprefix $(VIEWS_PATH)/, $(addsuffix .py, $(VIEWS_NAMES)))



default: help

.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: init
init: clean ## install project requrements into .venv
	pip3 install --upgrade pipenv
	-$(PIPENV) --rm
	if [[ $(shell uname) == 'Darwin' ]]; then \
	brew install openssl postgresql; \
	env LDFLAGS="-L$(shell brew --prefix openssl)/lib" CFLAGS="-I$(shell brew --prefix openssl)/include" $(PIPENV) install --python $(PYTHON) --dev --skip-lock; \
	else \
		$(PIPENV) install --python 3.6 --dev --skip-lock; \
	fi

	$(PIPENV) run pre-commit install

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
	$(PIPENV) run python3 -m jussi.serve  --debug=1 --server_workers=1 --upstream_config_file ALT_CONFIG.json

.PHONY: test
test: ## run all tests
	$(PIPENV) run pytest

.PHONY: test-with-docker
test-with-docker: Pipfile.lock build  ## run tests that depend on docker
	$(PIPENV) run pytest --rundocker --jussiurl http://localhost:8080

.PHONY: lint
lint: ## lint python files
	$(PIPENV) run pylint $(PROJECT_NAME)

.PHONY: fmt
fmt: ## format python files
    # yapf is disabled until the update 3.6 fstring compat
	$(PIPENV) run yapf --in-place --style pep8 --recursive $(PROJECT_NAME) tests
	$(PIPENV) run autopep8 --verbose --verbose --max-line-length=100 --aggressive --jobs -1 --in-place  --recursive $(PROJECT_NAME) tests

.PHONY: fix-imports
fix-imports: remove-unused-imports sort-imports ## remove unused and then sort imports

.PHONY: remove-unused-imports
remove-unused-imports: ## remove unused imports from python files
	$(PIPENV) run autoflake --in-place --remove-all-unused-imports --recursive $(PROJECT_NAME) tests

.PHONY: sort-imports
sort-imports: ## sorts python imports using isort with settings from .editorconfig
	$(PIPENV) run isort --verbose --recursive --atomic --settings-path  .editorconfig --virtual-env .venv $(PROJECT_NAME) tests

.PHONY: pipenv-check
pipenv-check: ## run pipenv's package security checker
	$(PIPENV) check

.PHONY: pre-commit-init
pre-commit-init: ## initialize pre-commit
	$(PIPENV) run pre-commit install

.PHONY: pre-commit
pre-commit: ## run pre-commit against modified files
	$(PIPENV) run pre-commit run

.PHONY: pre-commit-all
pre-commit-all: ## run pre-commit against all files
	$(PIPENV) run pre-commit run --all-files

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
	psql

.PHONY: reset-db
reset-db:
	$(PIPENV) run python -m sbds.cli db reset

.PHONY: init-db
init-db:
	$(PIPENV) run python -m sbds.cli db init

.PHONY: ipython
ipython:
	envdir envd $(PIPENV) run ipython -i sbds/storages/db/scripts/ipython_init.py

README.rst: docs/src/README.rst
	cd $(DOCS_DIR) && $(MAKE) README

# --- CODEGEN -- #
$(OPERATIONS_PATH)/%.py: $(TEMPLATES_PATH)/operations/operation_class.tmpl
	$(SBDS_BASE_CMD) codegen generate-operation $(*F) \
	--templates_path $(TEMPLATES_PATH) \
	--headers_path $(HEADERS_PATH) \
	--examples_path $(EXAMPLES_PATH) > $@


$(VIRTUAL_OPERATIONS_PATH)/%.py: $(TEMPLATES_PATH)/operations/operation_class.tmpl
	$(SBDS_BASE_CMD) codegen generate-operation $(*F) \
	--templates_path $(TEMPLATES_PATH) \
	--headers_path $(HEADERS_PATH) \
	--examples_path $(EXAMPLES_PATH) > $@

$(VIEWS_PATH)/%.py: $(TEMPLATES_PATH)/views/account_history_view.tmpl
	$(SBDS_BASE_CMD) codegen generate-operation $(*F) \
	--templates_path $(TEMPLATES_PATH) \
	--headers_path $(HEADERS_PATH) \
	--examples_path $(EXAMPLES_PATH) > $@


virtual-ops: $(VIRTUAL_OPERATION_PYTHON_FILES)
ops: $(OPERATION_PYTHON_FILES)

.PHONY: delete-virtual-ops
delete-virtual-ops:
	-rm $(VIRTUAL_OPERATION_PYTHON_FILES)

.PHONY: delete-ops
delete-ops:
	-rm $(OPERATION_PYTHON_FILES)

.PHONY: remove-ops
remove-ops: delete-ops delete-virtual-ops

.PHONY: build-ops
build-ops: ops virtual-ops

.PHONY: rebuild-ops
rebuild-ops: remove-ops build-ops

.PHONY: debug-CODEGEN_PATH
debug-CODEGEN_PATH:
	echo $(CODEGEN_PATH)

.PHONY: debug-OPERATIONS_PATH
debug-OPERATIONS_PATH:
	echo $(OPERATIONS_PATH)

.PHONY: debug-OPERATION_NAMES
debug-OPERATION_NAMES:
	echo $(OPERATION_NAMES)

.PHONY: debug-VIRTUAL-OPERATION_NAMES
debug-VIRTUAL-OPERATION_NAMES:
	echo $(VIRTUAL-OPERATION_NAMES)

.PHONY: debug-OPERATION_PYTHON_FILES
debug-OPERATION_PYTHON_FILES:
	echo $(OPERATION_PYTHON_FILES)

.PHONY: debug-VIRTUAL_OPERATION_PYTHON_FILES
debug-VIRTUAL_OPERATION_PYTHON_FILES:
	echo $(VIRTUAL_OPERATION_PYTHON_FILES)
