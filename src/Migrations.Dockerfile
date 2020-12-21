FROM python:3.8

RUN apt-get update -y && apt-get upgrade
COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app/
COPY src/rna /app/rna
COPY src/migrations /app/migrations
COPY src/manage.py .
ENV PYTHONPATH=/app

CMD ["python","manage.py", "db", "upgrade"]