#!/usr/bin/env python3
"""
Menedżer bota Telegram - uruchamianie, monitorowanie, zarządzanie
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path
from dotenv import load_dotenv


class BotManager:
    """Menedżer bota Telegram"""
    
    def __init__(self):
        self.bot_process = None
        self.pid_file = Path("telegram_bot.pid")
        load_dotenv()
    
    def start_bot(self):
        """Uruchamia bota"""
        if self.is_running():
            print("⚠️ Bot już działa!")
            return False
        
        print("🚀 Uruchamianie bota Telegram...")
        
        try:
            # Sprawdzamy konfigurację
            if not self.check_config():
                return False
            
            # Uruchamiamy bota w tle
            self.bot_process = subprocess.Popen([
                sys.executable, "telegram_bot.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Zapisujemy PID
            with open(self.pid_file, 'w') as f:
                f.write(str(self.bot_process.pid))
            
            print(f"✅ Bot uruchomiony! PID: {self.bot_process.pid}")
            print("📱 Bot jest gotowy do odbierania wiadomości")
            
            return True
            
        except Exception as e:
            print(f"❌ Błąd uruchamiania bota: {e}")
            return False
    
    def stop_bot(self):
        """Zatrzymuje bota"""
        if not self.is_running():
            print("⚠️ Bot nie działa!")
            return False
        
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                os.kill(pid, signal.SIGTERM)
                self.pid_file.unlink(missing_ok=True)
                
                print("✅ Bot zatrzymany!")
                return True
            else:
                print("❌ Nie można znaleźć PID bota!")
                return False
                
        except Exception as e:
            print(f"❌ Błąd zatrzymywania bota: {e}")
            return False
    
    def restart_bot(self):
        """Restartuje bota"""
        print("🔄 Restartowanie bota...")
        self.stop_bot()
        time.sleep(2)
        return self.start_bot()
    
    def is_running(self):
        """Sprawdza czy bot działa"""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Sprawdzamy czy proces istnieje
            os.kill(pid, 0)
            return True
            
        except (OSError, ValueError):
            # Proces nie istnieje, usuwamy plik PID
            self.pid_file.unlink(missing_ok=True)
            return False
    
    def get_status(self):
        """Pobiera status bota"""
        if self.is_running():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                return f"✅ Bot działa (PID: {pid})"
            except:
                return "❌ Bot nie działa"
        else:
            return "❌ Bot nie działa"
    
    def check_config(self):
        """Sprawdza konfigurację"""
        required_vars = ['TELEGRAM_BOT_TOKEN']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Brakujące zmienne środowiskowe: {', '.join(missing_vars)}")
            print("   Uruchom: python setup_bot.py")
            return False
        
        return True
    
    def show_logs(self, lines=50):
        """Pokazuje logi bota"""
        log_file = Path("telegram_bot.log")
        if not log_file.exists():
            print("❌ Plik logów nie istnieje!")
            return
        
        print(f"📋 Ostatnie {lines} linii logów:")
        print("-" * 50)
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                for line in last_lines:
                    print(line.rstrip())
        except Exception as e:
            print(f"❌ Błąd odczytu logów: {e}")
    
    def cleanup(self):
        """Czyści pliki tymczasowe"""
        temp_dir = Path("temp_videos")
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
            print("🧹 Wyczyszczono pliki tymczasowe")
        
        self.pid_file.unlink(missing_ok=True)
        print("🧹 Wyczyszczono pliki systemowe")


def main():
    """Główna funkcja menedżera"""
    manager = BotManager()
    
    if len(sys.argv) < 2:
        print("🤖 MENEDŻER BOTA TELEGRAM")
        print("=" * 40)
        print("Dostępne komendy:")
        print("  start    - Uruchom bota")
        print("  stop     - Zatrzymaj bota")
        print("  restart  - Restartuj bota")
        print("  status   - Status bota")
        print("  logs     - Pokaż logi")
        print("  cleanup  - Wyczyść pliki")
        print("  config   - Sprawdź konfigurację")
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        manager.start_bot()
    elif command == "stop":
        manager.stop_bot()
    elif command == "restart":
        manager.restart_bot()
    elif command == "status":
        print(manager.get_status())
    elif command == "logs":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        manager.show_logs(lines)
    elif command == "cleanup":
        manager.cleanup()
    elif command == "config":
        if manager.check_config():
            print("✅ Konfiguracja poprawna!")
        else:
            print("❌ Konfiguracja niepoprawna!")
    else:
        print(f"❌ Nieznana komenda: {command}")


if __name__ == "__main__":
    main()
