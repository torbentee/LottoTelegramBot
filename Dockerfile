FROM python:3.9-alpine as base
LABEL maintainer="torben.tietze@gmail.com"

FROM base as builder
RUN apk add --no-cache build-base make libressl-dev musl-dev libffi-dev
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY . /app
WORKDIR /app
CMD ["python", "bot.py"]
