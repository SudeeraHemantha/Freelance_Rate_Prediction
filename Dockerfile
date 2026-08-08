# Hugging Face Space Root Dockerfile for Freelance Rate Predictor Backend & UI
FROM python:3.10-slim

WORKDIR /code

# Install OpenMP runtime library required for LightGBM compilation/execution
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install system-wide
COPY backend/requirements-serving.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /code/requirements.txt

# Set up non-root user (UID 1000) for Hugging Face Spaces compatibility
RUN useradd -m -u 1000 user
USER user

# Set production environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/home/user/app/backend \
    PORT=7860 \
    ENV=production \
    DEBUG=false \
    CORS_ORIGINS="*" \
    DATABASE_URL="postgresql://neondb_owner:npg_0ECf3HIsFZmc@ep-little-sun-ayfuto9q-pooler.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

WORKDIR $HOME/app

# Copy entire project directory with non-root user permissions
COPY --chown=user:user . $HOME/app

EXPOSE 7860

# Run Gradio & FastAPI app on port 7860
CMD ["sh", "-c", "cd backend && uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}"]
