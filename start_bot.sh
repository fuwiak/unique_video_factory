#!/bin/bash
# Skrypt do uruchamiania bota w tle

# Aktywuj środowisko wirtualne
source .venv/bin/activate

# Sprawdź czy bot już działa
if pgrep -f "telegram_bot.py" > /dev/null; then
    echo "⚠️ Bot już działa!"
    echo "PID: $(pgrep -f telegram_bot.py)"
    exit 1
fi

# Uruchom bota w tle
echo "🚀 Uruchamianie bota w tle..."
nohup python telegram_bot.py > bot.log 2>&1 &

# Pobierz PID
BOT_PID=$!

# Zapisz PID do pliku
echo $BOT_PID > telegram_bot.pid

echo "✅ Bot uruchomiony w tle!"
echo "📱 PID: $BOT_PID"
echo "📋 Logi: bot.log"
echo "🛑 Aby zatrzymać: kill $BOT_PID"
