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

FROM base AS build

WORKDIR /app
RUN pip install -U poetry==1.1.14 -q -i https://mirrors.cloud.tencent.com/pypi/simple
COPY poetry.lock ./poetry.lock
COPY pyproject.toml ./pyproject.toml
RUN poetry install -q --no-dev --no-root

RUN EBIAN_FRONTEND=noninteractive apt update && poetry run python -m playwright install-deps && rm -rf /var/lib/apt/lists/*
RUN poetry run python -m playwright install



FROM build

WORKDIR /app
COPY ez ./ez

EXPOSE 8080
CMD poetry run uvicorn ez.main:app --port 8080 --host 0.0.0.0 --workers 4