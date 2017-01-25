IMAGE_NAME := sbdsimg

default: build

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run $(IMAGE_NAME)