

default: build

.PHONY: test run

build: pep8
	docker build -t steemit/sbds .

run:
	docker run steemit/sbds

test:
	python setup.py test

pep8-test:
	py.test --pep8 -m pep8

fmt:
	yapf --recursive .

pep8:
	pep8 .

