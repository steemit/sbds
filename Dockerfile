FROM phusion/baseimage:0.9.19

ENV DATABASE_URL sqlite:////tmp/sqlite.db
ENV STEEMD_HTTP_URL https://steemd.steemitdev.com
ENV SBDS_LOG_LEVEL INFO
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV APP_ROOT /app
ENV WSGI_APP ${APP_ROOT}/sbds/server/serve.py
ENV HTTP_SERVER_PORT 8080
ENV HTTP_SERVER_STATS_PORT 9191
ENV SBDS_ENVIRONMENT DEV

RUN \
    apt-get update && \
    apt-get install -y \
        build-essential \
        checkinstall \
        daemontools \
        git \
        libbz2-dev \
        libc6-dev \
        libffi-dev \
        libgdbm-dev \
        libmysqlclient-dev \
        libncursesw5-dev \
        libreadline-gplv2-dev \
        libsqlite3-dev \
        libssl-dev \
        libxml2-dev \
        libxslt-dev \
        nginx \
        nginx-extras \
        make \
        runit \
        tk-dev \
        wget && \
    apt-get clean


RUN \
    wget https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tar.xz && \
    tar xvf Python-3.6.4.tar.xz && \
    cd Python-3.6.4/ && \
    ./configure && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.6.4.tar.xz Python-3.6.4/

RUN apt-get install -y pip3

RUN pip3 install --upgrade pip

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
