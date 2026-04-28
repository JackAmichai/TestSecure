# Password Authentication Research Project
## מטלה תכנותית - קורס 20940 - ניתוח השוואתי של מנגנוני אימות מבוססי סיסמאות

### Project Overview

This project implements a comparative analysis of password-based authentication mechanisms, examining how different hashing algorithms and protection mechanisms perform against common attack methods such as Brute-Force and Password-Spraying.

### GROUP_SEED Calculation

The GROUP_SEED for this project is calculated as the **bitwise XOR** of two student ID numbers:

```python
# Example calculation:
ID1 = 123456789
ID2 = 987654321
GROUP_SEED = ID1 ^ ID2  # Result: 1067108368
```

**Current GROUP_SEED**: Please update `DEFAULT_GROUP_SEED` in `config_profiles.py` with your actual calculation.

The GROUP_SEED is used for:
- Uniqueness and integrity validation
- Originality checking
- Experiment reproducibility
- One of the passwords in the dataset equals the GROUP_SEED

### Project Structure

```
password-research/
├── app.py                  # Flask authentication server
├── config.py              # Configuration loader
├── config_profiles.py     # Configuration profiles for different experiments
├── generate_users.py      # User dataset generation
├── attack_bruteforce.py   # Brute-force attack simulation
├── attack_spray.py        # Password-spraying attack simulation
├── analyze_logs.py        # Log analysis and statistics
├── requirements.txt       # Python dependencies
├── data/
│   └── users.json        # Generated user dataset
├── logs/
│   └── attempts.log      # Authentication attempt logs
└── README.md             # This file
```

### Features Implemented

#### Hashing Algorithms
- **SHA-256** with per-user salt
- **bcrypt** (cost=12)
- **Argon2id** (time=1, memory=64MB, parallelism=1)
- **Pepper** support (global secret from environment variable)

#### Protection Mechanisms
- **Rate Limiting**: Limits requests per username in time window
- **Account Lockout**: Locks account after N failed attempts
- **CAPTCHA Simulation**: Requires token after threshold failures
- **TOTP**: Time-based One-Time Password (2FA)

#### Attack Simulations
- Brute-Force attacks (targeting single accounts)
- Password-Spraying attacks (testing common passwords across many accounts)

### Installation and Setup

#### 1. Clone the Repository

```bash
git clone git@github.com:JackAmichai/password-research.git
cd password-research
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Configure GROUP_SEED

Edit `config_profiles.py` and update `DEFAULT_GROUP_SEED` with your calculated XOR value:

```python
DEFAULT_GROUP_SEED = YOUR_ID1 ^ YOUR_ID2
```

#### 4. Set Environment Variables (Optional)

For experiments with Pepper:

```bash
# Windows PowerShell
$env:PEPPER = "your-secret-pepper-value"

# Linux/Mac
export PEPPER="your-secret-pepper-value"
```

### Running Experiments

#### Step 1: Generate User Dataset

```bash
python generate_users.py
```

This creates 30 users (10 weak, 10 medium, 10 strong passwords) in `data/users.json`.

#### Step 2: Start the Authentication Server

```bash
# Default configuration (sha256_open)
python app.py

# With specific configuration profile
# Windows PowerShell:
$env:APP_CONFIG = "bcrypt_lockout_rate" ; python app.py

# Linux/Mac:
APP_CONFIG=bcrypt_lockout_rate python app.py
```

Available profiles:
- `sha256_open` - SHA-256 without protections
- `sha256_lockout_rate` - SHA-256 with lockout + rate limit
- `sha256_full` - SHA-256 with all protections
- `bcrypt_open` - bcrypt without protections
- `bcrypt_lockout_rate` - bcrypt with lockout + rate limit
- `bcrypt_full` - bcrypt with all protections
- `argon2_open` - Argon2id without protections
- `argon2_lockout_rate` - Argon2id with lockout + rate limit
- `argon2_full` - Argon2id with all protections

#### Step 3: Run Attack Simulations

In a separate terminal:

```bash
# Brute-force attack
python attack_bruteforce.py

# Password-spraying attack
python attack_spray.py
```

#### Step 4: Analyze Results

```bash
python analyze_logs.py
```

### API Endpoints

- `GET /health` - Health check
- `POST /register` - Register new user
  ```json
  {"username": "user1", "password": "pass123"}
  ```
- `POST /login` - Standard login
  ```json
  {"username": "user1", "password": "pass123", "captcha_token": "optional"}
  ```
- `POST /login_totp` - Login with TOTP
  ```json
  {"username": "user1", "password": "pass123", "totp_code": "123456"}
  ```
- `GET /admin/get_captcha_token?group_seed=SEED&username=USER` - Get CAPTCHA token (for testing)

### Configuration Profiles

Each profile defines:
- `GROUP_SEED`: Unique identifier
- `HASH_MODE`: sha256 | bcrypt | argon2id
- `PROTECTIONS_FLAGS`: List of enabled protections
- `LOCKOUT_MAX_FAILURES`: Failed attempts before lockout
- `LOCKOUT_SECONDS`: Lockout duration
- `RATE_LIMIT_WINDOW_SECONDS`: Rate limit time window
- `RATE_LIMIT_MAX_REQUESTS`: Max requests per window
- `CAPTCHA_THRESHOLD`: Failed attempts before CAPTCHA required

### Password Strength Categories

- **Weak**: 7-8 digit numbers, simple lowercase strings
- **Medium**: 8-10 character alphanumeric mixed case
- **Strong**: 12-14 characters with symbols, mixed case, numbers

### Log Format

All authentication attempts are logged to `logs/attempts.log` in JSON format:

```json
{
  "timestamp": "2025-11-30T12:34:56.789Z",
  "username": "weak_user_01",
  "hash_mode": "sha256",
  "protections": ["lockout", "rate_limit"],
  "result": "login_success",
  "latency_ms": 2.5,
  "group_seed": 123456789
}
```

### Reproducibility

To reproduce experiments:

1. Use the same GROUP_SEED
2. Set the same APP_CONFIG profile
3. Use the same PEPPER value (if applicable)
4. Generate users with the same seed
5. Run attacks with the same parameters
6. All configuration and logs include GROUP_SEED for traceability

### Metrics Collected

- Total attempts
- Time to first success
- Attempts per second
- Success rate by password category
- Average latency per attempt
- Lockout events
- Rate limit triggers
- CAPTCHA challenges

### Ethical Guidelines

⚠️ **IMPORTANT**: This project is for educational purposes only.

- All experiments are conducted on **local/virtual systems only**
- **NO attacks on external networks or systems**
- **NO real user data** - only synthetic test data
- Compliance with course ethical guidelines

### Data Analysis

The `analyze_logs.py` script provides:
- Summary statistics by hash mode and protections
- Results breakdown (success/failure/locked/rate-limited)
- Average latency measurements
- Attempts per second calculations

### Extending the Project

Optional enhancements:
- Test different Argon2 parameters (memory, time, parallelism)
- Performance testing under resource constraints
- Additional attack types (SQL injection, XSS testing on inputs)
- Distributed attack simulation
- Offline attack simulations

### Dependencies

- **Flask**: Web framework for authentication server
- **bcrypt**: bcrypt hashing library
- **argon2-cffi**: Argon2 hashing library
- **pyotp**: TOTP implementation
- **requests**: HTTP client for attack scripts

### Troubleshooting

**Server won't start**: Check if port 5000 is available
```bash
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/Mac
```

**Import errors**: Ensure all dependencies are installed
```bash
pip install -r requirements.txt
```

**TOTP failures**: Ensure system time is synchronized

**Rate limiting too strict**: Adjust parameters in config_profiles.py

### Project Team

- Student 1: [ID]
- Student 2: [ID]
- GROUP_SEED: [Your calculated XOR value]

### License

This project is for academic use only as part of course 20940.

### References

- NIST SP 800-63B - Digital Identity Guidelines
- OWASP Password Storage Cheat Sheet
- RFC 6238 - TOTP: Time-Based One-Time Password Algorithm
- Microsoft Security Research - Password Spraying Attacks
