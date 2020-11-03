FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk add --no-cache gcc musl-dev && \
    pip3 install --no-cache-dir pipenv

COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock
RUN pipenv install --deploy --system && \
    apk --no-cache del gcc musl-dev && \
    pip3 uninstall -y pipenv

COPY atomic_counter /app/atomic_counter

HEALTHCHECK --interval=1m --timeout=3s CMD curl -sS 127.0.0.1:8888 || exit 1

CMD ["python3", "-m", "atomic_counter", "--datadir=./data"]
