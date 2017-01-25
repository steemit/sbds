FROM phusion/baseimage:0.9.19

ENV DATABASE_URL sqlite:////tmp/sqlite.db
ENV WEBSOCKET_URL wss://steemit.com/wspa
ENV STEEMD_HTTP_URL http://this.piston.rocks

ADD . /app

RUN \
    mv /app/service/* /etc/service && \
    chmod +x /etc/service/*/run

WORKDIR /app

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
        pv \
        python3 \
        python3-dev \
        python3-pip \
        runit && \
    pip3 install --upgrade pip && \
    pip3 install . && \
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

EXPOSE 8080