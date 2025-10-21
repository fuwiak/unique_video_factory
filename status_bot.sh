#!/bin/bash
# Skrypt do sprawdzania statusu bota

echo "🤖 STATUS BOTA TELEGRAM"
echo "=============================="

# Sprawdź czy plik PID istnieje
if [ -f telegram_bot.pid ]; then
    BOT_PID=$(cat telegram_bot.pid)
    echo "📋 PID z pliku: $BOT_PID"
    
    # Sprawdź czy proces działa
    if ps -p $BOT_PID > /dev/null 2>&1; then
        echo "✅ Bot działa (PID: $BOT_PID)"
        echo "📊 Użycie CPU: $(ps -p $BOT_PID -o %cpu | tail -1 | tr -d ' ')%"
        echo "📊 Użycie RAM: $(ps -p $BOT_PID -o %mem | tail -1 | tr -d ' ')%"
    else
        echo "❌ Bot nie działa (stary PID)"
        rm telegram_bot.pid
    fi
else
    echo "⚠️ Plik PID nie istnieje"
fi

# Sprawdź wszystkie procesy bota
BOT_PROCESSES=$(pgrep -f telegram_bot.py)
if [ ! -z "$BOT_PROCESSES" ]; then
    echo "📋 Znalezione procesy bota:"
    ps -p $BOT_PROCESSES -o pid,ppid,%cpu,%mem,etime,command 2>/dev/null || echo "Brak szczegółów procesów"
else
    echo "❌ Brak procesów bota"
fi

# Sprawdź logi
if [ -f bot.log ]; then
    echo "📋 Ostatnie 5 linii logów:"
    tail -5 bot.log
else
    echo "⚠️ Brak pliku logów"
fi
