FROM python:3.8

RUN apt-get update -y && apt-get upgrade
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN adduser celery
USER celery
WORKDIR /app/

COPY ./rna /app/rna
ENV PYTHONPATH=/app