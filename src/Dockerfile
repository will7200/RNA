FROM python:3.8

LABEL maintainer="William Flores <will7207@gmail.com>"

RUN apt-get update -y && apt-get upgrade
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN adduser rna
USER rna
WORKDIR /app/


COPY ./rna /app/rna
ENV PYTHONPATH=/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 5057
CMD ["gunicorn", "--name", "rna", "--bind", "0.0.0.0:5057", "rna.app:create_app(None)"]