# Advanced Configuration Guide

## config.yaml Detailed Explanation

### Search Criteria

```yaml
search_criteria:
  # Job titles to search for
  keywords:
    - "Python Developer"
    - "Backend Engineer"
    - "Full Stack Developer"
  
  # Must-have skills (higher weight in matching)
  required_skills:
    - "Python"
    - "Django"
    - "REST API"
  
  # Nice-to-have skills (bonus points)
  optional_skills:
    - "Docker"
    - "AWS"
    - "React"
  
  # Locations (can include "Remote")
  locations:
    - "Remote"
    - "New York, NY"
    - "San Francisco, CA"
  
  # Experience levels
  experience_level:
    - "Mid-Level"
    - "Senior"
    - "Lead"
  
  # Salary expectations
  salary_range:
    min: 100000  # Minimum acceptable
    max: 200000  # Maximum (optional)
  
  # Employment types
  job_types:
    - "Full-time"
    - "Contract"
    - "Contract-to-hire"
```

### Application Settings

```yaml
application:
  # Enable/disable auto-submission
  auto_apply: true  # Set to false to only fill forms without submitting
  
  # Path to your resume (relative to project root)
  resume_path: "resumes/resume.pdf"
  
  # Cover letter template
  cover_letter_template: "templates/cover_letter.txt"
  
  # Common application questions
  custom_answers:
    work_authorization: "Yes, I am authorized to work in the US"
    willing_to_relocate: "Yes"
    expected_salary: "150000"
    notice_period: "2 weeks"
    years_of_experience: "5"
    security_clearance: "No"
```

### Platform Settings

```yaml
platforms:
  dice:
    enabled: true
    max_applications_per_run: 10
    search_pages: 3  # Number of pages to scrape per search
  
  indeed:
    enabled: false
    max_applications_per_run: 10
    search_pages: 3
```

### Safety Settings

```yaml
safety:
  # Prevent duplicate applications
  duplicate_detection: true
  
  # Hours to wait before applying to same company again
  cooldown_period_hours: 24
  
  # Maximum applications per day (safety limit)
  max_applications_per_day: 20
  
  # Random delays between actions
  random_delay_enabled: true
  min_delay_seconds: 30
  max_delay_seconds: 90
```

### Scheduling

```yaml
schedule:
  enabled: true
  
  # Options: "daily", "hourly", or cron expression
  frequency: "daily"
  
  # Time in 24-hour format (for daily frequency)
  run_time: "09:00"
  
  # Examples of cron expressions:
  # "0 9 * * 1-5"  - Every weekday at 9 AM
  # "0 */3 * * *"  - Every 3 hours
  # "0 9,17 * * *" - At 9 AM and 5 PM
```

## Environment Variables (.env)

```bash
# Dice Platform Credentials
DICE_EMAIL=your_email@example.com
DICE_PASSWORD=your_secure_password

# Database
DATABASE_URL=sqlite:///jobider.db
# For PostgreSQL: postgresql://user:password@localhost/jobider

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Application Behavior
MAX_APPLICATIONS_PER_DAY=20
APPLICATION_DELAY_MIN=30
APPLICATION_DELAY_MAX=90

# Browser Settings
HEADLESS_MODE=true  # Set to false for debugging

# Notifications (optional)
ENABLE_NOTIFICATIONS=false
NOTIFICATION_EMAIL=alerts@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## Match Scoring System

Jobs are scored 0-100 based on:

- **Required Skills (40 points)**: Percentage of required skills found in job description
- **Optional Skills (20 points)**: Percentage of optional skills present
- **Location Match (20 points)**: Job location matches your preferences
- **Salary Match (20 points)**: Job salary meets your minimum

**Minimum threshold: 60%** - Jobs below this are skipped.

### Adjusting Scoring

To change the threshold, modify `src/adapters/dice_adapter.py`:

```python
# Line ~220
if match_score < 60:  # Change this value
    self.logger.debug(f"Job score too low: {match_score:.1f}%")
    return False
```

## Database Schema

The application uses SQLite by default. Tables:

1. **jobs** - All discovered job listings
2. **applications** - Application tracking
3. **user_profile** - Your profile data
4. **search_history** - Search performance metrics

### Viewing Database

```bash
sqlite3 jobider.db

# SQL commands:
SELECT * FROM applications ORDER BY applied_date DESC LIMIT 10;
SELECT company, COUNT(*) FROM jobs GROUP BY company;
SELECT status, COUNT(*) FROM applications GROUP BY status;
```

## Tips for Better Matching

### 1. Be Specific with Keywords
Instead of generic terms, use specific job titles:
```yaml
keywords:
  - "Senior Python Backend Engineer"
  - "Python Django Developer"
```

### 2. Balance Required vs Optional Skills
Too many required skills = fewer matches:
```yaml
required_skills:  # Keep this focused
  - "Python"
  - "Django"

optional_skills:  # Add variety here
  - "Docker"
  - "PostgreSQL"
  - "Redis"
  - "Celery"
```

### 3. Use Multiple Location Formats
```yaml
locations:
  - "Remote"
  - "New York, NY"
  - "New York City"
  - "NYC"
```

## Advanced Usage

### Run in Screen/Tmux for Long Sessions

```bash
screen -S jobider
source venv/bin/activate
python scheduler.py
# Ctrl+A then D to detach
```

### Cron Job (Linux/Mac)

```bash
crontab -e

# Add:
0 9 * * * cd /path/to/jobider && /path/to/jobider/venv/bin/python main.py
```

### Custom Platform Adapter

To add a new platform:

1. Create `src/adapters/newplatform_adapter.py`
2. Extend `BasePlatformAdapter`
3. Implement required methods
4. Add to `src/adapters/__init__.py`
5. Update `main.py` to include it

## Performance Optimization

### Speed Up Searches
- Reduce `search_pages` in config
- Use more specific keywords
- Limit locations

### Reduce Resource Usage
- Enable `HEADLESS_MODE=true`
- Reduce `max_applications_per_run`
- Increase delay between actions

## Troubleshooting

### High Memory Usage
Chrome can consume memory. Restart periodically:
```yaml
max_applications_per_run: 5  # Lower this
```

### Getting Blocked/CAPTCHA
- Increase delays
- Reduce application rate
- Use residential proxy (advanced)
- Add more random human-like actions

### Login Failures
- Check credentials
- Try manual login first
- Check for 2FA requirements
- Verify Dice account is active
