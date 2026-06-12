# ============================================================
# Production Dockerfile — Multi-stage, < 500 MB, non-root
# ============================================================

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

<<<<<<< HEAD
=======
RUN apt-get update && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

>>>>>>> 1bc3e8ea401ec09838476ee6810d4087387fcd6d
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Runtime
FROM python:3.11-slim AS runtime

# Non-root user
<<<<<<< HEAD
RUN groupadd -r agent && useradd -r -m -g agent -d /home/agent agent
=======
RUN groupadd -r agent && useradd -r -g agent -d /app agent
>>>>>>> 1bc3e8ea401ec09838476ee6810d4087387fcd6d

WORKDIR /app

# Copy packages từ builder
COPY --from=builder /root/.local /home/agent/.local

# Copy application
COPY app/ ./app/
<<<<<<< HEAD
=======
COPY utils/ ./utils/
>>>>>>> 1bc3e8ea401ec09838476ee6810d4087387fcd6d

RUN chown -R agent:agent /app

USER agent

ENV PATH=/home/agent/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c \
    "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" \
    || exit 1

<<<<<<< HEAD
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--timeout-graceful-shutdown", "30"]
=======
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
>>>>>>> 1bc3e8ea401ec09838476ee6810d4087387fcd6d
