# =========================================================
# Stage 1: Build virtual environment & install dependencies
# =========================================================
FROM python:3.10-slim AS builder

WORKDIR /build

# Install OpenMP runtime library required for LightGBM compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Setup virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy serving requirements and install lightweight dependencies
COPY requirements-serving.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --retries 10 --timeout 60 -r requirements.txt


# =========================================================
# Stage 2: Production runtime image
# =========================================================
FROM python:3.10-slim AS runner

WORKDIR /app

# Install OpenMP runtime library required for LightGBM execution
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set production environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    ENV=production

# Copy backend application source code into /app
COPY . /app

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

