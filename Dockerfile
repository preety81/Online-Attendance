# Dockerfile for Online Attendance App
# Build: docker build -t attendance-app:latest .
# Run: docker run -p 8501:8501 -e SUPABASE_URL=... -e SUPABASE_ANON_KEY=... attendance-app:latest

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for dlib, face-recognition, and librosa
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install setuptools constraint (required for face-recognition-models)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir 'setuptools<70.0.0'

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory with proper permissions
RUN mkdir -p .logs && chmod 777 .logs

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_MAXUPLOADSIZE=50
ENV STREAMLIT_LOGGER_LEVEL=info
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit app
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--client.showErrorDetails=false", "--client.showSidebarNavigation=true"]
