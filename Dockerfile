FROM python:3.5

#RUN apk add --no-cache mysql-client mysql

RUN mkdir -p /usr/src/app
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN pip install .

ENTRYPOINT sbds

