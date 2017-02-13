ROOT_DIR := .
DOCS_DIR := $(ROOT_DIR)/docs
DOCS_BUILD_DIR := $(DOCS_DIR)/_build


default: build

.PHONY: test run

build: pep8 README.rst
	docker build -t steemit/sbds .

run:
	docker run steemit/sbds

test:
	python setup.py test

pep8-test:
	py.test --pep8 -m pep8

fmt:
	yapf --recursive --in-place .
	autopep8 --recursive --in-place .
	
README.rst: docs/src/README.rst 
	cd docs
	$(MAKE) README