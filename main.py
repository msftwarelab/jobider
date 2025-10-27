"""
Main entry point for JobBider application
"""

import argparse
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils import load_config, load_env, setup_logger
from src.database import Database
from src.adapters import DiceAdapter


def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════╗
    ║         JobBider - v1.0.0             ║
    ║   Automated Job Application System    ║
    ╚═══════════════════════════════════════╝
    """
    print(banner)


def show_statistics(db):
    """Display application statistics"""
    stats = db.get_statistics()
    
    print("\n" + "="*50)
    print("APPLICATION STATISTICS")
    print("="*50)
    print(f"Total Jobs Discovered:     {stats['total_jobs_discovered']}")
    print(f"Total Applications:        {stats['total_applications']}")
    print(f"Successful Applications:   {stats['successful_applications']}")
    print(f"Failed Applications:       {stats['failed_applications']}")
    
    if stats['total_applications'] > 0:
        success_rate = (stats['successful_applications'] / stats['total_applications']) * 100
        print(f"Success Rate:              {success_rate:.1f}%")
    
    print("="*50 + "\n")


def run_platform(platform_name, config, db, search_only=False):
    """Run job search and application for a specific platform"""
    logger = setup_logger()
    
    if platform_name == 'dice':
        adapter = DiceAdapter(config, db)
    else:
        logger.error(f"Unsupported platform: {platform_name}")
        return False
    
    try:
        logger.info(f"Starting {platform_name} job search...")
        result = adapter.run(search_only=search_only)
        
        logger.info(f"Completed! Jobs found: {result['jobs_found']}, Applications: {result['applications_submitted']}")
        return True
        
    except Exception as e:
        logger.error(f"Error running {platform_name}: {str(e)}")
        return False


def main():
    """Main application entry point"""
    print_banner()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='JobBider - Automated Job Application System')
    parser.add_argument('--platform', '-p', 
                       choices=['dice', 'indeed', 'all'], 
                       default='all',
                       help='Platform to run (default: all)')
    parser.add_argument('--search-only', '-s', 
                       action='store_true',
                       help='Only search and save jobs, do not apply')
    parser.add_argument('--stats', 
                       action='store_true',
                       help='Show application statistics')
    parser.add_argument('--config', '-c',
                       default='config.yaml',
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Load environment and configuration
    load_env()
    
    try:
        config = load_config()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Initialize database
    db = Database()
    
    # Show statistics if requested
    if args.stats:
        show_statistics(db)
        return
    
    # Setup logger
    logger = setup_logger()
    
    # Determine which platforms to run
    platforms_to_run = []
    
    if args.platform == 'all':
        # Get enabled platforms from config
        for platform, settings in config['platforms'].items():
            if settings.get('enabled', False):
                platforms_to_run.append(platform)
    else:
        platforms_to_run = [args.platform]
    
    if not platforms_to_run:
        logger.error("No platforms enabled. Please check your config.yaml")
        sys.exit(1)
    
    logger.info(f"Running platforms: {', '.join(platforms_to_run)}")
    
    if args.search_only:
        logger.info("Search-only mode: Will not submit applications")
    
    # Run each platform
    success_count = 0
    for platform in platforms_to_run:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing platform: {platform.upper()}")
        logger.info(f"{'='*60}\n")
        
        success = run_platform(platform, config, db, args.search_only)
        if success:
            success_count += 1
    
    # Final summary
    logger.info(f"\n{'='*60}")
    logger.info(f"SESSION COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"Platforms processed: {success_count}/{len(platforms_to_run)}")
    
    # Show statistics
    show_statistics(db)
    
    logger.info("JobBider session ended. Check logs/ for detailed logs.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        logger = setup_logger()
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)
