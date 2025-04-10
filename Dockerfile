FROM python:3.10.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock README.md LICENSE /app/
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

COPY . /app

CMD ["poetry", "run", "englishAudioBot"]
