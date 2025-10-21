#!/bin/bash

# Start self-hosted Bot API server
# This script starts the telegram-bot-api server in the background

echo "🚀 Starting self-hosted Bot API server..."

# Check if API credentials are set
if [ -z "$TELEGRAM_API_ID" ] || [ -z "$TELEGRAM_API_HASH" ]; then
    echo "❌ TELEGRAM_API_ID or TELEGRAM_API_HASH not set"
    echo "   Please set these environment variables"
    exit 1
fi

# Check if telegram-bot-api binary exists
TELEGRAM_BOT_API_PATH=""
for path in "/usr/local/bin/telegram-bot-api" "/usr/bin/telegram-bot-api" "./telegram-bot-api"; do
    if [ -x "$path" ]; then
        TELEGRAM_BOT_API_PATH="$path"
        break
    fi
done

if [ -z "$TELEGRAM_BOT_API_PATH" ]; then
    echo "❌ telegram-bot-api binary not found"
    echo "   Please install it or run docker-compose up telegram-bot-api"
    exit 1
fi

echo "✅ Found telegram-bot-api at: $TELEGRAM_BOT_API_PATH"

# Start the server
echo "🚀 Starting server with API ID: $TELEGRAM_API_ID"
echo "   Port: 8081"
echo "   Verbosity: 1"

# Kill any existing server on port 8081
lsof -ti:8081 | xargs kill -9 2>/dev/null || true

# Start server in background
nohup "$TELEGRAM_BOT_API_PATH" \
    --api-id "$TELEGRAM_API_ID" \
    --api-hash "$TELEGRAM_API_HASH" \
    --local \
    --http-port 8081 \
    --verbosity 1 \
    > /tmp/telegram-bot-api.log 2>&1 &

SERVER_PID=$!
echo "✅ Server started with PID: $SERVER_PID"

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Check if server is running
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ Server is running"
    
    # Test if server responds
    if curl -s http://localhost:8081/health > /dev/null 2>&1; then
        echo "✅ Server is responding to health checks"
    else
        echo "⚠️ Server is running but not responding to health checks"
        echo "   This might be normal for some configurations"
    fi
    
    echo "🎯 Self-hosted Bot API is ready!"
    echo "   URL: http://localhost:8081"
    echo "   PID: $SERVER_PID"
    echo "   Logs: /tmp/telegram-bot-api.log"
else
    echo "❌ Server failed to start"
    echo "   Check logs: /tmp/telegram-bot-api.log"
    exit 1
fi
