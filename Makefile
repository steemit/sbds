ROOT_DIR := .
DOCS_DIR := $(ROOT_DIR)/docs
DOCS_BUILD_DIR := $(DOCS_DIR)/_build


default: build

.PHONY: test run

build: test README.rst
	docker build -t steemit/sbds .

run:
	docker run steemit/sbds

test:
	python setup.py test

pylint-test:
	py.test --pyline -m pylint

fmt:
	yapf --recursive --in-place --style pep8 .
	
README.rst: docs/src/README.rst 
	cd docs
	$(MAKE) README