# Installation & Testing Guide

## 🚀 Quick Installation

### Step 1: Setup Environment

```bash
# Navigate to project directory
cd /Users/cloud/Documents/MyData/Cloud/Work/jobider

# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

This will:
- Create virtual environment
- Install all dependencies
- Create necessary directories
- Initialize database
- Copy .env template

### Step 2: Configure Credentials

Edit `.env` file:
```bash
nano .env
```

Add your Dice credentials:
```bash
DICE_EMAIL=your_email@example.com
DICE_PASSWORD=your_password
```

### Step 3: Configure Preferences

Edit `config.yaml`:
```bash
nano config.yaml
```

Update these sections:
- `keywords`: Job titles you want
- `required_skills`: Your main skills
- `locations`: Where you want to work
- `salary_range`: Your salary expectations

### Step 4: Add Resume

```bash
# Copy your resume
cp /path/to/your/resume.pdf resumes/resume.pdf

# Verify
ls -l resumes/
```

## 🧪 Testing

### Test 1: Check Dependencies

```bash
source venv/bin/activate
python -c "import selenium, sqlalchemy, yaml; print('✓ All dependencies installed')"
```

### Test 2: Database Initialization

```bash
python -c "from src.database import Database; db = Database(); print('✓ Database working')"
```

### Test 3: Configuration Loading

```bash
python -c "from src.utils import load_config; config = load_config(); print('✓ Config loaded:', config['search_criteria']['keywords'])"
```

### Test 4: Search Only (No Applications)

**IMPORTANT**: Always test with search-only first!

```bash
# Activate virtual environment
source venv/bin/activate

# Run search only
python main.py --search-only
```

This will:
- Login to Dice
- Search for jobs matching your criteria
- Save jobs to database
- NOT submit any applications

Expected output:
```
╔═══════════════════════════════════════╗
║         JobBider - v1.0.0             ║
║   Automated Job Application System    ║
╚═══════════════════════════════════════╝

INFO - Starting dice job search...
INFO - Logging into Dice.com...
INFO - Successfully logged into Dice.com
INFO - Searching: 'Python Developer' in 'Remote'
INFO - Found 25 jobs
INFO - Job 'Senior Python Developer' matches criteria (score: 85.0%)
...
INFO - Session complete: Found 25 jobs, Applied to 0
```

### Test 5: View Statistics

```bash
python main.py --stats
```

Expected output:
```
==================================================
APPLICATION STATISTICS
==================================================
Total Jobs Discovered:     25
Total Applications:        0
Successful Applications:   0
Failed Applications:       0
==================================================
```

### Test 6: Check Database

```bash
sqlite3 jobider.db "SELECT title, company, location FROM jobs LIMIT 5;"
```

## 🎯 First Real Run

Once testing is successful:

### Option A: Manual Run (Recommended for first time)

```bash
# Set auto_apply to false in config.yaml first
nano config.yaml
# Change: auto_apply: false

# Run and review what it would apply to
python main.py

# If happy with results, enable auto_apply
nano config.yaml
# Change: auto_apply: true

# Run for real
python main.py
```

### Option B: Start with Low Limits

```yaml
# In config.yaml
safety:
  max_applications_per_day: 5  # Start small

platforms:
  dice:
    max_applications_per_run: 3  # Very conservative
```

Then run:
```bash
python main.py
```

## 🔍 Monitoring

### Watch Logs in Real-Time

```bash
# In another terminal
tail -f logs/jobider_*.log
```

### Check Application Status

```bash
sqlite3 jobider.db "SELECT job_id, success, applied_date FROM applications ORDER BY applied_date DESC LIMIT 10;"
```

### View Match Scores

```bash
sqlite3 jobider.db "SELECT title, company, match_score FROM applications ORDER BY match_score DESC LIMIT 10;"
```

## 🐛 Debugging

### Run in Non-Headless Mode

See the browser in action:

```bash
# In .env file
HEADLESS_MODE=false

# Run
python main.py --search-only
```

### Check Screenshots

If errors occur, screenshots are saved:
```bash
ls -l screenshots/
open screenshots/dice_*.png  # On macOS
```

### Verbose Logging

```bash
# In .env
LOG_LEVEL=DEBUG

# Run
python main.py --search-only
```

### Common Issues

**Issue: "Import X could not be resolved"**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Issue: "Chrome driver not found"**
```bash
pip install --upgrade webdriver-manager
```

**Issue: "Login failed"**
- Verify credentials in .env
- Check if Dice requires CAPTCHA
- Try manual login first
- Run with HEADLESS_MODE=false

**Issue: "No jobs found"**
- Check search criteria in config.yaml
- Try broader keywords
- Verify locations are correct
- Run with --search-only to debug

**Issue: "Match scores too low"**
- Add more optional_skills
- Reduce required_skills
- Adjust salary expectations
- Check keyword specificity

## 📊 Automated Scheduling

### Option 1: Scheduler Script

```bash
# Configure in config.yaml
schedule:
  enabled: true
  frequency: "daily"
  run_time: "09:00"

# Run scheduler
python scheduler.py
```

Scheduler runs in foreground. Use screen/tmux for background:
```bash
screen -S jobider
source venv/bin/activate
python scheduler.py
# Press Ctrl+A then D to detach
```

### Option 2: Cron Job

```bash
crontab -e

# Add (adjust path):
0 9 * * * cd /Users/cloud/Documents/MyData/Cloud/Work/jobider && /Users/cloud/Documents/MyData/Cloud/Work/jobider/venv/bin/python main.py >> /Users/cloud/Documents/MyData/Cloud/Work/jobider/logs/cron.log 2>&1
```

## ✅ Verification Checklist

Before running in production:

- [ ] Credentials configured in .env
- [ ] config.yaml customized with your preferences
- [ ] Resume added to resumes/resume.pdf
- [ ] Tested with --search-only
- [ ] Reviewed matched jobs in database
- [ ] Checked match scores are reasonable
- [ ] Set appropriate daily limits
- [ ] Tested one full application manually
- [ ] Logs directory created and writable
- [ ] Database initialized successfully
- [ ] Virtual environment activated

## 🎓 Learning the System

### Understand Match Scoring

```bash
# View jobs with scores
sqlite3 jobider.db "SELECT title, company, match_score FROM jobs ORDER BY match_score DESC LIMIT 20;"
```

### Analyze What Works

```bash
# See which companies you've applied to most
sqlite3 jobider.db "SELECT company, COUNT(*) as count FROM applications GROUP BY company ORDER BY count DESC;"

# Success rate by platform
sqlite3 jobider.db "SELECT platform, COUNT(*) as total, SUM(CASE WHEN success=1 THEN 1 ELSE 0 END) as successful FROM applications GROUP BY platform;"
```

### Optimize Over Time

1. Monitor which keywords find the most matches
2. Adjust required vs optional skills
3. Fine-tune match score thresholds
4. Experiment with different search locations
5. Track response rates (manual)

## 📈 Next Steps

Once comfortable:

1. **Increase limits**: Gradually raise daily application limits
2. **Add platforms**: Implement Indeed, LinkedIn adapters
3. **Automate**: Enable scheduler for hands-off operation
4. **Track results**: Monitor interview rates and optimize
5. **Customize**: Adjust matching algorithm for better results

## 🆘 Getting Help

Check these in order:

1. **Logs**: `logs/jobider_YYYYMMDD.log`
2. **Screenshots**: `screenshots/` directory
3. **Database**: Query to see what's stored
4. **Documentation**: README.md, ADVANCED.md
5. **Test mode**: Run with --search-only

## 🔒 Security Reminder

- Never commit `.env` file
- Don't share credentials
- Use strong, unique passwords
- Consider application-specific passwords
- Regularly rotate credentials
- Monitor for unauthorized access

## 🎉 Success Indicators

You'll know it's working when:

- ✅ Logs show successful logins
- ✅ Jobs are being discovered and saved
- ✅ Match scores are reasonable (60-90%)
- ✅ Applications are submitting successfully
- ✅ No error messages in logs
- ✅ Database is growing with jobs and applications

Good luck with your job search! 🚀
