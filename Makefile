SHELL := /bin/bash
ROOT_DIR := $(shell pwd)
DOCS_DIR := $(ROOT_DIR)/docs
DOCS_BUILD_DIR := $(DOCS_DIR)/_build

PROJECT := $(shell basename $(ROOT_DIR))

default: build

.PHONY: init build run test lint fmt name

init:
	pip3 install pipenv
	pipenv lock
	pipenv install --three --dev
	pipenv install .

build:
	docker build -t steemit/$(PROJECT) .

run:
	docker run steemit/$(PROJECT)

test:
	pipenv run py.test tests

lint:
	 pipenv run py.test --pylint -m pylint $(PROJECT)

fmt:
	pipenv run yapf --recursive --in-place --style pep8 $(PROJECT)
	pipenv run autopep8 --recursive --in-place $(PROJECT)

README.rst: docs/src/README.rst 
	cd $(DOCS_DIR) && $(MAKE) README
