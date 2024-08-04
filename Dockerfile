FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev

WORKDIR /app

COPY . /app

RUN pip install poetry
RUN poetry install

CMD ["poetry", "run", "python", "main.py"]