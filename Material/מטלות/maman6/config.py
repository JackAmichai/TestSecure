# config.py

import os
from config_profiles import CONFIGS

# נבחר פרופיל לפי משתנה סביבה APP_CONFIG, ברירת מחדל sha256_open
ACTIVE_CONFIG_NAME = os.getenv("APP_CONFIG", "sha256_open")

if ACTIVE_CONFIG_NAME not in CONFIGS:
    raise ValueError(f"Unknown config profile: {ACTIVE_CONFIG_NAME}")

_active = CONFIGS[ACTIVE_CONFIG_NAME]

# קבועים משותפים לכל הפרופילים
DATA_DIR = "data"
LOGS_DIR = "logs"
USERS_FILE = "users.json"
ATTEMPTS_LOG_FILE = "attempts.log"

# ערכים שתלויים בפרופיל
GROUP_SEED = _active["GROUP_SEED"]
HASH_MODE = _active["HASH_MODE"]
PROTECTIONS_FLAGS = _active["PROTECTIONS_FLAGS"]

LOCKOUT_MAX_FAILURES = _active["LOCKOUT_MAX_FAILURES"]
LOCKOUT_SECONDS = _active["LOCKOUT_SECONDS"]

RATE_LIMIT_WINDOW_SECONDS = _active["RATE_LIMIT_WINDOW_SECONDS"]
RATE_LIMIT_MAX_REQUESTS = _active["RATE_LIMIT_MAX_REQUESTS"]

CAPTCHA_THRESHOLD = _active.get("CAPTCHA_THRESHOLD", 3)

# Pepper - global secret loaded from environment, not stored in DB
PEPPER = os.getenv("PEPPER", "")

