# SafeTrade ELT pipeline in a container.
# Build once:   docker build -t safetrade .
# Run:          docker run --rm -v "$(pwd)/reports:/app/reports" safetrade
# Full guide:   docs/4-runbook.md (section "Run with Docker")

FROM python:3.12-slim

# No .pyc files, and logs appear straight away.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib

WORKDIR /app

# Install packages first. Docker caches this layer, so changing the
# code later does not reinstall everything.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the project.
COPY pipeline/ pipeline/
COPY sql/ sql/
COPY tests/ tests/
COPY data/sample/ data/sample/
COPY pytest.ini .

# Run as a normal user, not root.
RUN useradd --create-home --uid 1000 pipeline \
    && mkdir -p reports/charts data/landing data/warehouse \
    && chown -R pipeline:pipeline /app
USER pipeline

# Default: run the whole pipeline on the anonymised sample.
# Override the command to run tests or use the live sheet.
CMD ["python", "-m", "pipeline.run"]
