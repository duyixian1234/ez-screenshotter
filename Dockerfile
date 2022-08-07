FROM python:3.10-slim AS base

WORKDIR /tmp
RUN sed -i 's#deb.debian.org#mirrors.cloud.tencent.com#' /etc/apt/sources.list
RUN DEBIAN_FRONTEND=noninteractive apt update && apt install fontconfig wget -y \
    && wget http://httpredir.debian.org/debian/pool/contrib/m/msttcorefonts/ttf-mscorefonts-installer_3.8_all.deb \
    && apt install ./ttf-mscorefonts-installer_3.8_all.deb -y \
    && apt remove ./ttf-mscorefonts-installer_3.8_all.deb -y \
    && rm ./ttf-mscorefonts-installer_3.8_all.deb \
    && mkfontscale && mkfontdir && fc-cache -fv \
    && apt remove fontconfig wget -y

FROM base AS deps
ADD ./requirements.txt /tmp/requirements.txt
RUN set -xe && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone && \
    pip install --no-cache-dir -r /tmp/requirements.txt -q

FROM deps AS build
RUN set -xe \
    && sed -i 's#security.debian.org#mirrors.cloud.tencent.com#' /etc/apt/sources.list \
    && DEBIAN_FRONTEND=noninteractive apt update \
    && python -m playwright install-deps \
    && rm -rf /var/lib/apt/lists/*
RUN python -m playwright install
WORKDIR /app
COPY ez ./ez


FROM build
WORKDIR /app
EXPOSE 8080
CMD uvicorn ez.main:app --port 8080 --host 0.0.0.0 --workers 4