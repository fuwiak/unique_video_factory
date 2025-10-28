# Dockerfile for Railway deployment with conditional self-hosted API
# Build argument to control self-hosted API installation
ARG USE_SELF_HOSTED_API=true

# Multi-stage build for telegram-bot-api (only if needed)
FROM ubuntu:22.04 AS telegram-bot-api-builder
ARG USE_SELF_HOSTED_API
RUN if [ "$USE_SELF_HOSTED_API" = "true" ]; then \
        echo "🔧 Building telegram-bot-api..." && \
        apt-get update && apt-get install -y \
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
            && rm -rf /var/lib/apt/lists/* && \
        git clone --recursive https://github.com/tdlib/telegram-bot-api.git /tmp/telegram-bot-api && \
        cd /tmp/telegram-bot-api && \
        mkdir build && \
        cd build && \
        cmake .. && \
        make -j$(nproc) && \
        cp telegram-bot-api /usr/local/bin/telegram-bot-api; \
    else \
        echo "⚠️ Skipping telegram-bot-api build (USE_SELF_HOSTED_API=false)"; \
    fi

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

# Copy telegram-bot-api from builder stage (only if it exists)
ARG USE_SELF_HOSTED_API
RUN if [ "$USE_SELF_HOSTED_API" = "true" ]; then \
        echo "📦 Copying telegram-bot-api..." && \
        cp /usr/local/bin/telegram-bot-api /usr/local/bin/telegram-bot-api 2>/dev/null || \
        echo "⚠️ telegram-bot-api not found, skipping..."; \
    else \
        echo "⚠️ Skipping telegram-bot-api copy (USE_SELF_HOSTED_API=false)"; \
    fi

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

# Self-hosted API flag (set to false to disable)
ENV USE_SELF_HOSTED_API=${USE_SELF_HOSTED_API}

# Expose ports (Railway will set PORT env var)
EXPOSE 8000 8081 8082

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Create startup script for Railway
RUN echo '#!/bin/bash\n\
echo "🚀 Starting Telegram bot..."\n\
\n\
# Check if self-hosted API should be enabled\n\
if [ "$USE_SELF_HOSTED_API" = "false" ] || [ "$USE_SELF_HOSTED_API" = "0" ]; then\n\
    echo "⚠️ Self-hosted Bot API is disabled (USE_SELF_HOSTED_API=$USE_SELF_HOSTED_API)"\n\
    echo "   Starting bot with standard Telegram API..."\n\
else\n\
    echo "🔧 Starting self-hosted Bot API server..."\n\
    \n\
    # Check if telegram-bot-api exists\n\
    if [ ! -f "/usr/local/bin/telegram-bot-api" ]; then\n\
        echo "❌ telegram-bot-api not found! Please rebuild with USE_SELF_HOSTED_API=true"\n\
        echo "   Falling back to standard Telegram API..."\n\
    else\n\
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
    fi\n\
fi\n\
\n\
echo "🤖 Starting Telegram bot..."\n\
exec python telegram_bot.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]