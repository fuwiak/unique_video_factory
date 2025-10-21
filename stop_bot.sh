#!/bin/bash
# Skrypt do zatrzymywania bota

# Sprawdź czy plik PID istnieje
if [ -f telegram_bot.pid ]; then
    BOT_PID=$(cat telegram_bot.pid)
    echo "🛑 Zatrzymywanie bota (PID: $BOT_PID)..."
    
    # Zatrzymaj bota
    kill $BOT_PID 2>/dev/null
    
    # Usuń plik PID
    rm telegram_bot.pid
    
    echo "✅ Bot zatrzymany!"
else
    echo "⚠️ Plik PID nie istnieje, szukam procesu..."
    
    # Znajdź i zatrzymaj proces
    BOT_PID=$(pgrep -f telegram_bot.py)
    if [ ! -z "$BOT_PID" ]; then
        echo "🛑 Zatrzymywanie bota (PID: $BOT_PID)..."
        kill $BOT_PID
        echo "✅ Bot zatrzymany!"
    else
        echo "❌ Bot nie działa!"
    fi
fi
