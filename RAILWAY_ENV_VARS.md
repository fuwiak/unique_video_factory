# Railway Environment Variables

## How to Disable Self-Hosted Bot API Temporarily

To disable the self-hosted Bot API and use standard Telegram API (20MB limit):

1. **Go to Railway Dashboard** → Your Project → Variables
2. **Add or Update:**
   ```
   USE_SELF_HOSTED_API = false
   ```
3. **Save** and Railway will auto-redeploy

## Environment Variables

### Required Variables
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `YANDEX_DISK_TOKEN` - Yandex Disk token (optional)

### Optional Variables

#### Self-Hosted Bot API Control
- `USE_SELF_HOSTED_API` - Enable/disable self-hosted API
  - `true` - Use self-hosted API (2GB limit) - **Default**
  - `false` - Use standard Telegram API (20MB limit)

#### Self-Hosted API Configuration
- `TELEGRAM_API_ID` - Telegram API ID (required for self-hosted)
- `TELEGRAM_API_HASH` - Telegram API HASH (required for self-hosted)
- `SELF_HOSTED_API_URL` - URL of self-hosted API (default: http://localhost:8081)
- `MAX_FILE_SIZE_MB` - Max file size in MB (default: 2000)

#### Other Settings
- `YANDEX_DISK_FOLDER` - Yandex Disk folder name
- `MAX_VIDEO_SIZE_MB` - Max video size in MB
- `PORT` - Port for health check (Railway auto-sets this)

## Quick Toggle

To quickly switch between self-hosted API and standard API:

```bash
# Disable self-hosted API (use standard Telegram API)
railway variables set USE_SELF_HOSTED_API=false

# Enable self-hosted API (use 2GB limit)
railway variables set USE_SELF_HOSTED_API=true
```

## Why Use Standard API?

- **Faster deployment** - No need to build telegram-bot-api
- **Lower resource usage** - Less memory and CPU
- **Simpler setup** - No need for TELEGRAM_API_ID and TELEGRAM_API_HASH
- **20MB limit** - All files must be under 20MB

## Why Use Self-Hosted API?

- **2GB limit** - Can send large files
- **Better performance** - For large video files
- **More control** - Custom configuration

