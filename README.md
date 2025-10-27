# JobBider - Automated Job Application System

An intelligent automation tool for applying to jobs on platforms like Dice, Indeed, and more.

## Features

- 🎯 **Smart Job Matching** - Filters jobs based on your skills and preferences
- 🤖 **Automated Applications** - Auto-fills and submits job applications
- 📊 **Application Tracking** - Keeps track of all your applications
- 🔒 **Duplicate Prevention** - Never applies to the same job twice
- ⏰ **Scheduled Runs** - Set it and forget it
- 🛡️ **Safe & Ethical** - Respects rate limits and platform guidelines

## Setup

1. **Clone and Install Dependencies**
   ```bash
   cd jobider
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Customize Job Preferences**
   Edit `config.yaml` with your job search criteria, skills, and preferences.

4. **Add Your Resume**
   Place your resume in `resumes/resume.pdf`

## Usage

### Basic Usage
```bash
python main.py
```

### Search for Jobs (without applying)
```bash
python main.py --search-only
```

### Run with specific platform
```bash
python main.py --platform dice
```

### View Statistics
```bash
python main.py --stats
```

## Configuration

### config.yaml
Main configuration file for:
- Job search criteria (keywords, skills, locations)
- Application settings (resume path, custom answers)
- Platform-specific settings
- Scheduling preferences

### .env
Environment variables for:
- Platform credentials (encrypted)
- Database connection
- Application behavior settings

## Project Structure

```
jobider/
├── main.py                 # Main entry point
├── config.yaml            # User configuration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── src/
│   ├── __init__.py
│   ├── database/          # Database models and operations
│   ├── adapters/          # Platform-specific adapters
│   ├── matching/          # Job matching engine
│   ├── automation/        # Application automation logic
│   └── utils/             # Utility functions
├── logs/                  # Application logs
└── resumes/              # Your resume files
```

## Important Notes

⚠️ **Legal & Ethical Use**
- Always check the Terms of Service of each platform
- Use responsibly and within rate limits
- This tool is for educational purposes
- Ensure you meet the qualifications before applying

⚠️ **Security**
- Never commit your .env file
- Use strong, unique passwords
- Keep your credentials secure

## Troubleshooting

### Chrome Driver Issues
The application uses `webdriver-manager` which automatically downloads the correct ChromeDriver. If you encounter issues:
```bash
pip install --upgrade webdriver-manager
```

### Database Issues
To reset the database:
```bash
rm jobider.db
python main.py  # Will recreate the database
```

## Contributing

This is a personal automation tool. Use at your own discretion.

## License

MIT License - Use responsibly and ethically.
