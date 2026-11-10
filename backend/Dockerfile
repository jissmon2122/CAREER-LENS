FROM python:3.12-slim

# Set environment variables (enforce single-thread CPU execution to fit Render 512MB RAM)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000 \
    UPLOAD_FOLDER=uploads/resumes \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    VECLIB_MAXIMUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    TORCH_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false

# Install essential system dependencies for OpenCV, PyMuPDF, and ONNX Runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0t64 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-cache SentenceTransformer model to eliminate cold-start download latency on Render
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" || true

# Copy backend application source code
COPY . /app/

# Create upload directory
RUN mkdir -p /app/uploads/resumes

EXPOSE 5000

# Run with Gunicorn WSGI server: exactly 1 worker with 4 threads, recycled every 500 requests to permanently stay within 512MB RAM
CMD ["sh", "-c", "gunicorn wsgi:app --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 4 --worker-class gthread --max-requests 500 --max-requests-jitter 50 --timeout 120"]
