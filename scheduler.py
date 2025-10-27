"""
Scheduler for automated job applications
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils import load_config, load_env, setup_logger
from src.database import Database
from src.adapters import DiceAdapter


def run_job_search():
    """Run automated job search and application"""
    logger = setup_logger('scheduler')
    logger.info("Starting scheduled job search...")
    
    try:
        # Load configuration
        config = load_config()
        db = Database()
        
        # Get enabled platforms
        for platform_name, settings in config['platforms'].items():
            if not settings.get('enabled', False):
                continue
            
            logger.info(f"Running {platform_name}...")
            
            if platform_name == 'dice':
                adapter = DiceAdapter(config, db)
                result = adapter.run(search_only=False)
                logger.info(f"Completed {platform_name}: {result['applications_submitted']} applications")
        
        logger.info("Scheduled job search completed successfully")
        
    except Exception as e:
        logger.error(f"Error in scheduled job: {str(e)}")


def main():
    """Main scheduler entry point"""
    load_env()
    config = load_config()
    logger = setup_logger('scheduler')
    
    schedule_config = config.get('schedule', {})
    
    if not schedule_config.get('enabled', False):
        logger.error("Scheduling is not enabled in config.yaml")
        sys.exit(1)
    
    frequency = schedule_config.get('frequency', 'daily')
    run_time = schedule_config.get('run_time', '09:00')
    
    # Create scheduler
    scheduler = BlockingScheduler()
    
    if frequency == 'daily':
        hour, minute = run_time.split(':')
        scheduler.add_job(
            run_job_search,
            CronTrigger(hour=int(hour), minute=int(minute)),
            id='job_search',
            name='Daily Job Search',
            replace_existing=True
        )
        logger.info(f"Scheduler configured: Daily at {run_time}")
    
    elif frequency == 'hourly':
        scheduler.add_job(
            run_job_search,
            'interval',
            hours=1,
            id='job_search',
            name='Hourly Job Search',
            replace_existing=True
        )
        logger.info("Scheduler configured: Every hour")
    
    else:
        # Assume it's a cron expression
        scheduler.add_job(
            run_job_search,
            CronTrigger.from_crontab(frequency),
            id='job_search',
            name='Custom Job Search',
            replace_existing=True
        )
        logger.info(f"Scheduler configured: {frequency}")
    
    logger.info("Scheduler started. Press Ctrl+C to exit.")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
