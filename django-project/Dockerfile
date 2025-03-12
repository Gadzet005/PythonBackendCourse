FROM python:3.10.16-alpine3.21

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED 1

WORKDIR /backend/
COPY . /backend/

RUN pip install -r requirements.txt