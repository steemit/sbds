FROM python:3.5-alpine

RUN apk add --no-cache --virtual .build-deps \
    build-base \
    python3-dev \
    gcc \
    make \
    libffi-dev \
    openssl-dev \
    && apk add --no-cache bash mariadb-dev

RUN mkdir -p /usr/src/app
COPY base_requirements.txt /user/src/app/base_requirements.txt
RUN pip install -r /user/src/app/base_requirements.txt

COPY . /usr/src/app
WORKDIR /usr/src/app
RUN pip install . && apk del .build-deps

CMD ["sbds"]