default: build

build: test
	docker build -t steemit/sbds .

run:
	docker run steemit/sbds

test:
	python setup.py test
