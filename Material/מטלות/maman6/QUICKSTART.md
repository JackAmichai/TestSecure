# Quick Start Guide
## מדריך התחלה מהירה

### Prerequisites / דרישות מקדימות

1. Python 3.8 or higher
2. Git (for cloning repository)
3. pip (Python package manager)

### Step-by-Step Setup / התקנה צעד אחר צעד

#### 1. Clone the Repository / שיבוט הפרויקט

```bash
git clone git@github.com:JackAmichai/password-research.git
cd password-research
```

#### 2. Install Dependencies / התקנת תלויות

```bash
pip install -r requirements.txt
```

#### 3. Configure GROUP_SEED / הגדרת GROUP_SEED

**IMPORTANT:** Calculate your GROUP_SEED first!

```python
# Calculate XOR of two student IDs
ID1 = 123456789  # Replace with actual ID
ID2 = 987654321  # Replace with actual ID
GROUP_SEED = ID1 ^ ID2
print(f"Your GROUP_SEED: {GROUP_SEED}")
```

Edit `config_profiles.py` and update `DEFAULT_GROUP_SEED`:

```python
DEFAULT_GROUP_SEED = YOUR_CALCULATED_VALUE
```

#### 4. (Optional) Set PEPPER / הגדרת Pepper (אופציונלי)

**Windows PowerShell:**
```powershell
$env:PEPPER = "your-secret-pepper-value"
```

**Linux/Mac:**
```bash
export PEPPER="your-secret-pepper-value"
```

#### 5. Generate User Dataset / יצירת מסד נתונים

```bash
python generate_users.py
```

Expected output:
```
Generated 30 users into data\users.json
All users hashed with mode: sha256
```

#### 6. Start the Server / הפעלת השרת

**Terminal 1 - Start Server:**

```bash
# Default configuration (sha256_open)
python app.py
```

Or with specific configuration:

**Windows PowerShell:**
```powershell
$env:APP_CONFIG = "bcrypt_lockout_rate"
python app.py
```

**Linux/Mac:**
```bash
APP_CONFIG=bcrypt_lockout_rate python app.py
```

Server should start on `http://127.0.0.1:5000`

#### 7. Run Attacks / הרצת תקיפות

**Terminal 2 - Run Attacks:**

```bash
# Brute-force attack
python attack_bruteforce_enhanced.py

# Password spraying attack
python attack_spray_enhanced.py
```

#### 8. Analyze Results / ניתוח תוצאות

```bash
python analyze_logs_enhanced.py
```

### Running Full Experiment Suite / הרצת סדרת ניסויים מלאה

To run all configurations automatically:

```bash
python run_all_experiments.py
```

This will:
- Test all 9 configuration profiles
- Run both brute-force and spraying attacks
- Analyze results for each
- Save everything to `experiment_results/` directory

**Note:** This can take several hours to complete!

### Quick Test / בדיקה מהירה

Want to test if everything works? Run a quick test:

```bash
# Terminal 1: Start server
python app.py

# Terminal 2: Quick brute force test
python attack_bruteforce.py

# Check logs
python analyze_logs.py
```

### Available Configuration Profiles / פרופילי קונפיגורציה זמינים

| Profile | Hash Algorithm | Protections |
|---------|---------------|-------------|
| `sha256_open` | SHA-256 | None |
| `sha256_lockout_rate` | SHA-256 | Lockout + Rate Limit |
| `sha256_full` | SHA-256 | All (Lockout + Rate + CAPTCHA) |
| `bcrypt_open` | bcrypt | None |
| `bcrypt_lockout_rate` | bcrypt | Lockout + Rate Limit |
| `bcrypt_full` | bcrypt | All |
| `argon2_open` | Argon2id | None |
| `argon2_lockout_rate` | Argon2id | Lockout + Rate Limit |
| `argon2_full` | Argon2id | All |

### Testing TOTP (2FA) / בדיקת TOTP

To test TOTP authentication:

1. Check a user's TOTP secret in `data/users.json`
2. Generate TOTP code using Python:

```python
import pyotp
secret = "JBSWY3DPEHPK3PXP"  # From users.json
totp = pyotp.TOTP(secret)
print(f"Current TOTP code: {totp.now()}")
```

3. Test login:

```bash
curl -X POST http://127.0.0.1:5000/login_totp \
  -H "Content-Type: application/json" \
  -d '{"username":"weak_user_01", "password":"42400147", "totp_code":"123456"}'
```

### Viewing Logs / צפייה בלוגים

**Attempt logs:**
```bash
cat logs/attempts.log | head -20
```

**Analysis summary:**
```bash
cat logs/analysis_summary.json
```

### Troubleshooting / פתרון בעיות

#### Server won't start
```bash
# Check if port is in use
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/Mac

# Kill process if needed
# Windows: taskkill /PID <PID> /F
# Linux/Mac: kill <PID>
```

#### Import errors
```bash
pip install --upgrade -r requirements.txt
```

#### No users generated
Make sure you're in the project directory and `data/` folder exists.

#### Attack script fails
Make sure server is running first!

```bash
# Test server health
curl http://127.0.0.1:5000/health
```

Should return: `{"status":"ok"}`

### File Structure Overview / מבנה קבצים

```
password-research/
├── app.py                          # Flask server
├── config.py                       # Config loader
├── config_profiles.py              # Profile definitions
├── generate_users.py               # User generator
├── attack_bruteforce.py           # Simple brute force
├── attack_bruteforce_enhanced.py  # Enhanced brute force
├── attack_spray.py                # Simple spraying
├── attack_spray_enhanced.py       # Enhanced spraying
├── analyze_logs.py                # Basic analysis
├── analyze_logs_enhanced.py       # Advanced analysis
├── run_all_experiments.py         # Automation script
├── requirements.txt               # Dependencies
├── README.md                      # Full documentation
├── QUICKSTART.md                  # This file
├── ETHICS.md                      # Ethical declaration
├── REPORT_TEMPLATE.md            # Report template
├── data/
│   └── users.json                # Generated users
├── logs/
│   ├── attempts.log              # Authentication attempts
│   └── analysis_summary.json    # Analysis results
└── experiment_results/           # Automated experiment results
```

### Next Steps / צעדים הבאים

1. **Review the assignment requirements** in the main document
2. **Calculate your GROUP_SEED** properly
3. **Run baseline experiments** with different hash algorithms
4. **Test protection mechanisms** one at a time
5. **Collect comprehensive data** for all configurations
6. **Analyze results** thoroughly
7. **Write your report** using REPORT_TEMPLATE.md
8. **Sign the ethical declaration** in ETHICS.md
9. **Prepare presentation** and demo video

### Useful Commands / פקודות שימושיות

```bash
# Count total attempts
cat logs/attempts.log | wc -l

# Count successful logins
grep "success" logs/attempts.log | wc -l

# Count failed attempts
grep "fail" logs/attempts.log | wc -l

# View specific user attempts
grep "weak_user_01" logs/attempts.log

# Clear all logs
rm logs/attempts.log logs/analysis_summary.json

# Regenerate users (e.g., after changing hash mode)
python generate_users.py

# Check server is running
curl http://127.0.0.1:5000/health
```

### Tips for Success / טיפים להצלחה

1. **Start simple:** Test basic configurations first
2. **Keep logs organized:** Use different log files for different experiments
3. **Document everything:** Take notes as you go
4. **Test incrementally:** Add one protection at a time
5. **Backup your data:** Copy logs before clearing them
6. **Monitor server:** Watch for errors in server output
7. **Be patient:** Some experiments take time
8. **Read the assignment carefully:** Make sure you meet all requirements

### Getting Help / קבלת עזרה

1. Check README.md for detailed documentation
2. Review assignment requirements document
3. Contact your instructor or TA
4. Check course forum

### Important Reminders / תזכורות חשובות

⚠️ **Ethics:** Only test on your own systems  
⚠️ **GROUP_SEED:** Must be XOR of two student IDs  
⚠️ **Logs:** Save all logs for submission  
⚠️ **Report:** Use provided template  
⚠️ **Deadline:** Check course website  

### Good Luck! / בהצלחה!

You're all set! Follow the steps above and you'll have a successful project.

Remember:
- Work systematically
- Document thoroughly
- Test carefully
- Analyze critically
- Write clearly

---

**Created:** November 2025  
**Course:** 20940 - Introduction to Cybersecurity  
**Assignment:** Programming Assignment #16
