FROM phusion/baseimage:0.9.19

ENV DATABASE_URL sqlite:////tmp/sqlite.db
ENV WEBSOCKET_URL wss://steemd.steemitdev.com:443
ENV STEEMD_HTTP_URL https://steemd.steemitdev.com
ENV SBDS_LOG_LEVEL INFO
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV APP_ROOT /app
ENV WSGI_APP ${APP_ROOT}/sbds/server/serve.py
ENV HTTP_SERVER_PORT 8080
ENV HTTP_SERVER_PROCESSES 4
ENV HTTP_SERVER_THREADS  4
ENV HTTP_SERVER_STATS_PORT 9191
ENV SBDS_ENVIRONMENT DEV

RUN \
    apt-get update && \
    apt-get install -y \
        build-essential \
        daemontools \
        git \
        libffi-dev \
        libmysqlclient-dev \
        libssl-dev \
        make \
        python3 \
        python3-dev \
        python3-pip \
        libxml2-dev \
        libxslt-dev \
        runit

RUN \
    pip3 install --upgrade pip && \
    pip3 install uwsgi

ADD . /app

RUN \
    mv /app/service/* /etc/service && \
    chmod +x /etc/service/*/run

WORKDIR /app

RUN \

    pip3 install  . && \
    apt-get remove -y \
        build-essential \
        libffi-dev \
        libssl-dev && \
    apt-get autoremove -y && \
    rm -rf \
        /root/.cache \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /var/cache/* \
        /usr/include \
        /usr/local/include

EXPOSE ${HTTP_SERVER_PORT}
EXPOSE ${HTTP_SERVER_STATS_PORT}