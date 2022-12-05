FROM python:3.11-alpine as base

FROM base as builder
RUN apk add --no-cache build-base make libressl-dev musl-dev libffi-dev

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt


FROM base AS run-image
COPY --from=builder /opt/venv /opt/venv
COPY . .

ENV PATH="/opt/venv/bin:$PATH"
CMD ["python", "bot.py"]
