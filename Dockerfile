FROM python:3.12-alpine
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

EXPOSE 8000
WORKDIR /opt/app
COPY . .

RUN apk update \
    && apk add git \
    && uv sync --frozen

ENTRYPOINT [ "uv", "run", "python", "examples/github_app.py" ]
