# Quick Start Guide

## Installation

1. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure your credentials:**
   Edit `.env` file:
   ```bash
   nano .env
   ```
   Add your Dice.com credentials:
   ```
   DICE_EMAIL=your_email@example.com
   DICE_PASSWORD=your_password
   ```

3. **Configure your preferences:**
   Edit `config.yaml`:
   ```bash
   nano config.yaml
   ```
   Update:
   - Keywords (job titles you're looking for)
   - Required skills
   - Locations (Remote, specific cities)
   - Salary range
   - Custom answers for common questions

4. **Add your resume:**
   ```bash
   cp /path/to/your/resume.pdf resumes/resume.pdf
   ```

## Usage Examples

### Basic Usage - Search and Apply
```bash
python main.py
```

### Search Only (Don't Apply)
```bash
python main.py --search-only
```

### Run Specific Platform
```bash
python main.py --platform dice
```

### View Statistics
```bash
python main.py --stats
```

## Scheduled Automation

To run automatically on a schedule:

1. Edit `config.yaml` and enable scheduling:
   ```yaml
   schedule:
     enabled: true
     frequency: "daily"
     run_time: "09:00"
   ```

2. Run the scheduler:
   ```bash
   python scheduler.py
   ```

The application will now run automatically at the specified time.

## Tips

### Test First
Always test with `--search-only` first to see what jobs match:
```bash
python main.py --search-only
```

### Check Logs
View detailed logs:
```bash
tail -f logs/jobider_*.log
```

### Safety Features
- **Daily limit**: Max applications per day (default: 20)
- **Duplicate prevention**: Won't apply to same job twice
- **Random delays**: Human-like behavior to avoid detection
- **Match scoring**: Only applies to jobs with >60% match

### Troubleshooting

**Chrome Driver Issues:**
```bash
pip install --upgrade webdriver-manager
```

**Database Issues:**
```bash
rm jobider.db
python main.py  # Will recreate
```

**Can't login to Dice:**
- Verify credentials in `.env`
- Try manually logging in to check for CAPTCHA
- Run with `HEADLESS_MODE=false` to see what's happening

## Configuration Tips

### Match More Jobs
Lower the match threshold or add more optional skills:
```yaml
optional_skills:
  - "Docker"
  - "Kubernetes"
  - "AWS"
  # Add more...
```

### Be More Selective
Increase required skills and be specific with keywords:
```yaml
required_skills:
  - "Python"
  - "Django"
  - "PostgreSQL"
  - "REST API"
```

### Remote Only
Set locations to just Remote:
```yaml
locations:
  - "Remote"
```

## Important Notes

⚠️ **Legal Compliance**
- Always check platform Terms of Service
- Use responsibly
- Ensure you qualify for jobs you apply to

⚠️ **Security**
- Never commit `.env` file
- Keep credentials secure
- Use strong passwords

⚠️ **Detection Avoidance**
- Don't set application limits too high
- Use realistic delays
- Monitor for CAPTCHA challenges

## Need Help?

Check the logs in `logs/` directory for detailed information about what's happening.
