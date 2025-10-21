# Dockerfile for telegram-bot-api
FROM ubuntu:22.04

# Install dependencies
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
    curl \
    && rm -rf /var/lib/apt/lists/*

# Build telegram-bot-api
RUN git clone --recursive https://github.com/tdlib/telegram-bot-api.git /tmp/telegram-bot-api \
    && cd /tmp/telegram-bot-api \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make -j$(nproc) \
    && cp telegram-bot-api /usr/local/bin/telegram-bot-api \
    && rm -rf /tmp/telegram-bot-api

# Create non-root user
RUN useradd -m -s /bin/bash telegram

# Switch to non-root user
USER telegram

# Expose port
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# Run telegram-bot-api
CMD ["telegram-bot-api", "--local", "--http-port=8081", "--log-level=1"]
