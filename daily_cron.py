#!/usr/bin/env python3
"""
Daily cron service - runs daily_views_report.py periodically
Works with Railway cron or any scheduler
"""
import time
import logging
import schedule
from daily_views_report import DailyViewsReporter

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_daily_report():
    """Uruchamia daily report"""
    logger.info("🚀 Uruchamianie daily views reporter")
    
    reporter = DailyViewsReporter()
    
    if not reporter.sheet:
        logger.error("❌ Nie można połączyć z Google Sheets")
        return
    
    # Process all videos
    success = reporter.process_all_videos()
    
    if success:
        logger.info("✅ Raport codzienny zakończony pomyślnie")
    else:
        logger.error("❌ Błąd podczas tworzenia raportu")

def main():
    """Main function"""
    logger.info("⏰ Daily cron service started")
    
    # Schedule daily report at midnight UTC (00:00)
    schedule.every().day.at("00:00").do(run_daily_report)
    
    logger.info("📅 Daily report scheduled for 00:00 UTC")
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()

