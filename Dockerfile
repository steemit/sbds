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
ENV PIPENV_DEFAULT_PYTHON_VERSION 3.6.4

ENV NGINX_SERVER_PORT 8080

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
        lua-zlib \
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

# nginx
RUN \
  mkdir -p /var/lib/nginx/body && \
  mkdir -p /var/lib/nginx/scgi && \
  mkdir -p /var/lib/nginx/uwsgi && \
  mkdir -p /var/lib/nginx/fastcgi && \
  mkdir -p /var/lib/nginx/proxy && \
  chown -R www-data:www-data /var/lib/nginx && \
  mkdir -p /var/log/nginx && \
  touch /var/log/nginx/access.log && \
  touch /var/log/nginx/access.json && \
  touch /var/log/nginx/error.log && \
  chown www-data:www-data /var/log/nginx/* && \
  touch /var/run/nginx.pid && \
  chown www-data:www-data /var/run/nginx.pid && \
  mkdir -p /var/www/.cache && \
  chown www-data:www-data /var/www/.cache

RUN \
    python3.6 -m pip install --upgrade pip && \
    python3.6 -m pip install pipenv

COPY . /app

RUN \
    mv /app/service/* /etc/service && \
    chmod +x /etc/service/*/run

WORKDIR /app

RUN pipenv install --python 3.6 --dev

RUN \
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
