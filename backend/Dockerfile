# Hugging Face Space Dockerfile for Freelance Rate Predictor FastAPI Backend
FROM python:3.10-slim

WORKDIR /code

# Install OpenMP runtime library required for LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements system-wide
COPY requirements.txt requirements-serving.txt /code/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-serving.txt

# Set up non-root user (UID 1000) for Hugging Face Spaces compatibility
RUN useradd -m -u 1000 user
USER user

# Set environment variables for production execution
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    ENV=production \
    DEBUG=false \
    CORS_ORIGINS="*" \
    DATABASE_URL="postgresql://neondb_owner:npg_0ECf3HIsFZmc@ep-little-sun-ayfuto9q-pooler.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

WORKDIR $HOME/app

# Copy application files with proper non-root user permissions
COPY --chown=user:user . $HOME/app

# Expose default Hugging Face Space port
EXPOSE 7860

# Run FastAPI with Uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
