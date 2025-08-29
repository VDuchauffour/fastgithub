ARG PYTHON_VERSION=3.13

FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-alpine

EXPOSE 8000
WORKDIR /opt/app
COPY . .

RUN apk update \
    && apk add git \
    && uv python pin $PYTHON_VERSION \
    && uv sync --frozen

ENTRYPOINT [ "uv", "run", "python", "scripts/github_app.py" ]
