# Project Structure

```
jobider/
│
├── main.py                      # Main CLI application
├── scheduler.py                 # Automated scheduler
├── setup.sh                     # Setup script
├── requirements.txt             # Python dependencies
├── config.yaml                  # User configuration
├── .env                         # Environment variables (not in git)
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
│
├── README.md                    # Main documentation
├── QUICKSTART.md               # Quick start guide
├── ADVANCED.md                 # Advanced configuration
├── STRUCTURE.md                # This file
│
├── src/                        # Source code
│   ├── __init__.py
│   │
│   ├── database/               # Database layer
│   │   ├── __init__.py
│   │   └── models.py          # SQLAlchemy models
│   │
│   ├── adapters/              # Platform adapters
│   │   ├── __init__.py
│   │   ├── base_adapter.py   # Abstract base class
│   │   └── dice_adapter.py   # Dice.com implementation
│   │
│   ├── matching/              # Job matching engine
│   │   ├── __init__.py
│   │   └── matcher.py        # Matching logic
│   │
│   └── utils/                 # Utilities
│       ├── __init__.py
│       ├── helpers.py         # Helper functions
│       └── logger.py          # Logging configuration
│
├── templates/                  # Templates
│   └── cover_letter.txt       # Cover letter template
│
├── resumes/                   # Your resume files
│   └── resume.pdf            # Place your resume here
│
├── logs/                      # Application logs (auto-created)
│   └── jobider_YYYYMMDD.log
│
├── screenshots/               # Debug screenshots (auto-created)
│
└── jobider.db                # SQLite database (auto-created)
```

## Component Overview

### Core Files

**main.py**
- Command-line interface
- Entry point for manual runs
- Argument parsing and execution flow

**scheduler.py**
- Automated scheduling using APScheduler
- Cron-based job execution
- Background automation

**config.yaml**
- User preferences and search criteria
- Platform-specific settings
- Application behavior configuration

**.env**
- Sensitive credentials
- Platform login information
- Environment-specific settings

### Source Code (src/)

**database/models.py**
- SQLAlchemy ORM models
- Database schema definitions
- Data access methods

**adapters/base_adapter.py**
- Abstract base class for all platforms
- Common Selenium/WebDriver setup
- Shared automation methods
- Error handling and logging

**adapters/dice_adapter.py**
- Dice.com-specific implementation
- Login automation
- Job search and scraping
- Application form filling
- Platform-specific selectors

**matching/matcher.py**
- Job matching algorithm
- Scoring system (0-100)
- Criteria filtering

**utils/helpers.py**
- Utility functions
- Salary parsing
- Configuration loading
- Random delays

**utils/logger.py**
- Logging configuration
- File and console handlers
- Colored output

## Data Flow

```
1. User Configuration (config.yaml, .env)
   ↓
2. Main Entry Point (main.py)
   ↓
3. Platform Adapter (dice_adapter.py)
   ↓
4. Selenium WebDriver (Browser automation)
   ↓
5. Job Discovery (Search and scrape)
   ↓
6. Job Matching (matcher.py)
   ↓
7. Database Storage (models.py)
   ↓
8. Application Submission (dice_adapter.py)
   ↓
9. Results Tracking (Database)
```

## Key Classes

### Database Models
- `Job` - Job listing information
- `Application` - Application tracking
- `UserProfile` - User information
- `SearchHistory` - Search analytics
- `Database` - Database manager

### Adapters
- `BasePlatformAdapter` - Base class for all platforms
- `DiceAdapter` - Dice.com implementation

### Utilities
- `JobMatcher` - Job matching engine
- Various helper functions for common tasks

## Extension Points

### Adding a New Platform

1. Create `src/adapters/newplatform_adapter.py`
2. Inherit from `BasePlatformAdapter`
3. Implement required methods:
   - `platform_name` (property)
   - `login()`
   - `search_jobs(keywords, location)`
   - `extract_job_details(element)`
   - `apply_to_job(job_url, job_data)`

4. Register in `src/adapters/__init__.py`
5. Add to platform selection in `main.py`
6. Update `config.yaml` with platform settings

### Adding Custom Matching Logic

Edit `src/utils/helpers.py` → `calculate_match_score()` function

### Adding Notifications

Extend `main.py` or create `src/notifications/` module

### Custom Application Forms

Override or extend `fill_application_form()` in platform adapter

## Configuration Files

### config.yaml
- Job search criteria
- Platform settings
- Application preferences
- Safety limits
- Scheduling

### .env
- Credentials (encrypted storage recommended)
- Environment-specific settings
- Feature flags

## Database Schema

**jobs**
- id, platform, job_id, title, company
- location, job_type, salary_min, salary_max
- description, requirements, url
- posted_date, discovered_date

**applications**
- id, job_id, platform, applied_date
- status, match_score, application_method
- success, error_message, notes

**user_profile**
- id, full_name, email, phone
- resume_path, skills, experience_years
- work_authorization, expected_salary

**search_history**
- id, platform, search_date, keywords
- jobs_found, applications_submitted
- execution_time_seconds

## Logging

Logs are written to:
- **File**: `logs/jobider_YYYYMMDD.log` (all levels)
- **Console**: INFO and above (colored)

Log levels:
- DEBUG: Detailed information
- INFO: General progress
- WARNING: Issues that don't stop execution
- ERROR: Problems that affect functionality
- CRITICAL: Serious failures

## Best Practices

1. **Start with --search-only**: Test matching before applying
2. **Review logs regularly**: Check for issues
3. **Monitor application rate**: Don't exceed platform limits
4. **Update selectors**: Web pages change, update CSS selectors
5. **Backup database**: Save jobider.db periodically
6. **Use version control**: Track config changes
7. **Test in non-headless mode**: Debug visual issues
8. **Respect rate limits**: Avoid getting blocked

## Security Considerations

- ✅ `.env` in `.gitignore`
- ✅ Credentials never logged
- ✅ Database contains sensitive data
- ⚠️ Consider encrypting `.env`
- ⚠️ Use application-specific passwords
- ⚠️ Enable 2FA where possible (may require manual intervention)

## Performance Notes

- Chrome WebDriver uses ~100-200MB RAM per instance
- Headless mode saves ~50MB RAM
- Database grows ~1KB per job, ~500 bytes per application
- Logs can grow large, rotate regularly

## Future Enhancements

- [ ] Indeed platform adapter
- [ ] LinkedIn platform adapter
- [ ] Email notifications
- [ ] Web dashboard (Flask/React)
- [ ] Cover letter AI generation
- [ ] Interview tracking
- [ ] Salary analytics
- [ ] Application success predictor
- [ ] Multi-account support
- [ ] Proxy support for scaling
