FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install shared package
COPY pyproject.toml ./shared-pyproject.toml
COPY core ./core
RUN mv shared-pyproject.toml pyproject.toml && \
    pip install --no-cache-dir .[sql] && \
    rm pyproject.toml

# Install service package
COPY services/itinerary-service/pyproject.toml ./pyproject.toml
RUN pip install --no-cache-dir -e .

COPY services/itinerary-service/app ./app

RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
