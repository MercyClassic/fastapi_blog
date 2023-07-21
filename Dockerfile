FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTEDECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /blog

COPY ./pyproject.toml /blog/pyproject.toml

RUN apt update \
    && pip install poetry \
    && apt install -y nano \
    && apt install -y libmagic1 \
    && useradd -U app \
    && chown -R app:app /blog \
    && chdir /blog \
    && poetry config virtualenvs.create false \
    && poetry install --only main

WORKDIR /blog/src

COPY --chown=app:app . /blog

EXPOSE 8000

USER app

CMD ["sh", "/blog/entrypoint.sh"]
