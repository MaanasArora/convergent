FROM python:3.12

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"

WORKDIR /app
COPY . /app

RUN pip install engine-dist/convergent_engine-0.1.1-py3-none-any.whl

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

EXPOSE 8000

# Make entrypoint.sh executable
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint script
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]

# Run uvicorn server
CMD ["uvicorn", "convergent.main:app", "--host", "0.0.0.0", "--port", "8000"]
