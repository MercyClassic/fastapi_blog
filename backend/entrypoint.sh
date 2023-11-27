#!/bin/bash
cd /blog
alembic upgrade head
cd /blog/src
gunicorn main.main:app --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
