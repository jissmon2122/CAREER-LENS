FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000 \
    UPLOAD_FOLDER=uploads/resumes

# Install essential system dependencies for OpenCV, PyMuPDF, and ONNX Runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download default spaCy English model for NLP text processing
RUN python -m spacy download en_core_web_sm || true

# Copy backend application source code
COPY . /app/

# Create upload directory
RUN mkdir -p /app/uploads/resumes

EXPOSE 5000

# Run with Gunicorn WSGI server in production
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "120"]
