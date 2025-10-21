# Dockerfile for Railway deployment
# Multi-stage build for telegram-bot-api
FROM ubuntu:22.04 AS telegram-bot-api-builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libssl-dev \
    zlib1g-dev \
    gperf \
    libreadline-dev \
    libsqlite3-dev \
    libcurl4-openssl-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    && rm -rf /var/lib/apt/lists/*

# Build telegram-bot-api
RUN git clone --recursive https://github.com/tdlib/telegram-bot-api.git /tmp/telegram-bot-api \
    && cd /tmp/telegram-bot-api \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make -j$(nproc) \
    && cp telegram-bot-api /usr/local/bin/telegram-bot-api

# Main image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy telegram-bot-api from builder stage
COPY --from=telegram-bot-api-builder /usr/local/bin/telegram-bot-api /usr/local/bin/telegram-bot-api
RUN chmod +x /usr/local/bin/telegram-bot-api

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p temp_videos telegram_results generated_videos

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=2
ENV MKL_NUM_THREADS=2
ENV OPENBLAS_NUM_THREADS=2
ENV VECLIB_MAXIMUM_THREADS=2
ENV NUMEXPR_NUM_THREADS=2

# Expose port (Railway will set PORT env var)
EXPOSE 8000 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Create startup script for Railway
RUN echo '#!/bin/bash\n\
echo "🚀 Starting self-hosted Bot API server..."\n\
\n\
# Start telegram-bot-api in background\n\
if [ -n "$TELEGRAM_API_ID" ] && [ -n "$TELEGRAM_API_HASH" ]; then\n\
    echo "✅ Starting telegram-bot-api with API ID: $TELEGRAM_API_ID"\n\
    /usr/local/bin/telegram-bot-api \\\n\
        --api-id "$TELEGRAM_API_ID" \\\n\
        --api-hash "$TELEGRAM_API_HASH" \\\n\
        --local \\\n\
        --http-port 8081 \\\n\
        --verbosity 1 &\n\
    \n\
    # Wait for API to start\n\
    echo "⏳ Waiting for self-hosted API to start..."\n\
    sleep 10\n\
    \n\
    # Check if API is running\n\
    if curl -s http://localhost:8081/health > /dev/null 2>&1; then\n\
        echo "✅ Self-hosted Bot API is running"\n\
    else\n\
        echo "⚠️ Self-hosted Bot API may not be responding"\n\
    fi\n\
else\n\
    echo "⚠️ TELEGRAM_API_ID or TELEGRAM_API_HASH not set"\n\
    echo "   Self-hosted API will not start"\n\
fi\n\
\n\
echo "🤖 Starting Telegram bot..."\n\
exec python telegram_bot.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]
