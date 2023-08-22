FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTEDECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /blog

COPY ../backend/pyproject.toml /blog/pyproject.toml
COPY ./entrypoint.sh /blog/entrypoint.sh

RUN apt update \
    && pip install poetry \
    && apt install -y vim \
    && apt install -y libmagic1 \
    && useradd -U app \
    && chown -R app:app /blog \
    && chdir /blog \
    && poetry config virtualenvs.create false

RUN poetry install --only main

WORKDIR /blog/src

COPY --chown=app:app . /blog

EXPOSE 8000

USER app

CMD ["sh", "/blog/entrypoint.sh"]
