FROM python:3.5-alpine

RUN mkdir -p /usr/src/app

COPY . /usr/src/app

WORKDIR /usr/src/app

RUN apk add --no-cache --virtual .build-deps \
    build-base \
    python3-dev \
    mariadb-dev \
    gcc \
    make \
    libffi-dev \
    openssl-dev \
    && pip install . \
	&& apk del .build-deps

ENTRYPOINT ["sbds"]