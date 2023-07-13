FROM python:3.10.8

ENV PYTHONDONTWRITEBYTEDECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /home/app/blog/requirements.txt

RUN pip install --upgrade pip &&  \
    apt update && apt install -y nano && \
    pip install -r /home/app/blog/requirements.txt

RUN useradd -U app && \
    chown -R app:app /home/app

WORKDIR /home/app/blog

COPY --chown=app:app . .

EXPOSE 8000

USER app

CMD ["sh", "entrypoint.sh"]
