from flask import Flask, request, jsonify
import hashlib
import os
import json
import time
import datetime

import bcrypt
from argon2 import PasswordHasher, exceptions as argon2_exceptions
import pyotp

from config import (
    GROUP_SEED,
    HASH_MODE,
    DATA_DIR,
    LOGS_DIR,
    USERS_FILE,
    ATTEMPTS_LOG_FILE,
    PROTECTIONS_FLAGS,
    LOCKOUT_MAX_FAILURES,
    LOCKOUT_SECONDS,
    RATE_LIMIT_WINDOW_SECONDS,
    RATE_LIMIT_MAX_REQUESTS,
    CAPTCHA_THRESHOLD,
    PEPPER,
)

app = Flask(__name__)

USERS_PATH = os.path.join(DATA_DIR, USERS_FILE)
ATTEMPTS_LOG_PATH = os.path.join(LOGS_DIR, ATTEMPTS_LOG_FILE)

# יצירת תיקיות אם לא קיימות
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Argon2 helper with assignment parameters
# Parameters: time=1, memory=64MB, parallelism=1
ph = PasswordHasher(time_cost=1, memory_cost=65536, parallelism=1)

# מעקב lockout בזיכרון: username -> {"count": int, "locked_until": float}
failed_attempts = {}

# מעקב rate limit: username -> [timestamps]
rate_limits = {}

# מעקב CAPTCHA: username -> failed_count
captcha_required = {}

# CAPTCHA tokens מחוללים: username -> token
captcha_tokens = {}


# ========================
#   עזר: ניהול משתמשים
# ========================
def load_users():
    """
    טוען משתמשים מקובץ JSON.
    מחזיר מילון {username: user_record}
    """
    if not os.path.exists(USERS_PATH):
        return {}

    with open(USERS_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

    if isinstance(data, list):
        return {u["username"]: u for u in data}
    elif isinstance(data, dict):
        return data
    else:
        return {}


def save_users(users_dict):
    """
    שומר את המילון לקובץ כ-list של רשומות.
    """
    users_list = list(users_dict.values())
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users_list, f, ensure_ascii=False, indent=2)


# ========================
#   עזר: hashing כללי
# ========================
def hash_password(password: str, salt: str, hash_mode: str) -> str:
    """
    מחזיר hash של (pepper + salt + password) לפי hash_mode:
    sha256 / bcrypt / argon2id
    """
    combo = (PEPPER + salt + password).encode("utf-8")

    if hash_mode == "sha256":
        return hashlib.sha256(combo).hexdigest()

    elif hash_mode == "bcrypt":
        # bcrypt מחזיר bytes – נשמור כמחרוזת
        return bcrypt.hashpw(combo, bcrypt.gensalt()).decode("utf-8")

    elif hash_mode == "argon2id":
        # Argon2 מכיל מלח פנימי, אנחנו מוסיפים גם salt חיצוני לשמירה על אחידות
        return ph.hash(combo.decode("utf-8"))

    else:
        raise ValueError(f"Unsupported hash_mode: {hash_mode}")


def verify_password(password: str, salt: str, hash_mode: str, stored_hash: str) -> bool:
    """
    בודק האם password תואמת ל-stored_hash לפי hash_mode.
    """
    combo = (PEPPER + salt + password).encode("utf-8")

    if hash_mode == "sha256":
        candidate = hashlib.sha256(combo).hexdigest()
        return candidate == stored_hash

    elif hash_mode == "bcrypt":
        try:
            return bcrypt.checkpw(combo, stored_hash.encode("utf-8"))
        except ValueError:
            return False

    elif hash_mode == "argon2id":
        try:
            ph.verify(stored_hash, combo.decode("utf-8"))
            return True
        except argon2_exceptions.VerifyMismatchError:
            return False
        except argon2_exceptions.VerificationError:
            return False

    else:
        raise ValueError(f"Unsupported hash_mode: {hash_mode}")


# ========================
#   עזר: lockout
# ========================
def is_account_locked(username: str) -> bool:
    """
    מחזיר True אם החשבון נעול כרגע.
    אם זמן הנעילה עבר – מאפס את הסטטוס.
    """
    info = failed_attempts.get(username)
    if not info:
        return False

    locked_until = info.get("locked_until", 0.0)
    now = time.time()

    if locked_until > now:
        return True

    # אם הנעילה הסתיימה – נאפס מונה
    if locked_until and locked_until <= now:
        failed_attempts[username] = {"count": 0, "locked_until": 0.0}

    return False


def register_failed_login(username: str):
    """
    רישום כישלון התחברות – מעלה מונה, ואם חצה סף → נועל.
    """
    if not username:
        return

    now = time.time()
    info = failed_attempts.get(username, {"count": 0, "locked_until": 0.0})

    # אם כבר נעול ולא פג הזמן – לא משנים
    if info.get("locked_until", 0.0) > now:
        failed_attempts[username] = info
        return

    info["count"] = info.get("count", 0) + 1

    if info["count"] >= LOCKOUT_MAX_FAILURES:
        info["locked_until"] = now + LOCKOUT_SECONDS

    failed_attempts[username] = info


def reset_failed_logins(username: str):
    """
    איפוס מונה כישלונות אחרי הצלחה.
    """
    failed_attempts.pop(username, None)


# ========================
#   עזר: rate limiting
# ========================
def register_request(username: str):
    """
    רושם מתי בוצעה בקשה עבור המשתמש.
    אם אין username (למשל שדה חסר) – נשתמש במפתח 'global'.
    מופעל רק אם 'rate_limit' מופיע ב-PROTECTIONS_FLAGS.
    """
    if "rate_limit" not in PROTECTIONS_FLAGS:
        return

    key = username or "global"
    now = time.time()
    timestamps = rate_limits.get(key, [])
    timestamps.append(now)
    rate_limits[key] = timestamps


def is_rate_limited(username: str) -> bool:
    """
    בודק האם המשתמש עבר את מספר הבקשות המותר בחלון הזמן.
    """
    if "rate_limit" not in PROTECTIONS_FLAGS:
        return False

    key = username or "global"
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    timestamps = rate_limits.get(key, [])
    # נשאיר רק בקשות שנמצאות בתוך החלון
    timestamps = [t for t in timestamps if t >= window_start]
    rate_limits[key] = timestamps

    return len(timestamps) > RATE_LIMIT_MAX_REQUESTS


# ========================
#   עזר: CAPTCHA
# ========================
def check_captcha_required(username: str) -> bool:
    """
    בודק האם CAPTCHA נדרש עבור המשתמש הזה.
    """
    if "captcha" not in PROTECTIONS_FLAGS:
        return False
    
    count = captcha_required.get(username, 0)
    return count >= CAPTCHA_THRESHOLD


def register_captcha_failure(username: str):
    """
    מגדיל מונה כישלונות עבור CAPTCHA.
    """
    if "captcha" not in PROTECTIONS_FLAGS:
        return
    
    captcha_required[username] = captcha_required.get(username, 0) + 1


def reset_captcha(username: str):
    """
    מאפס מונה CAPTCHA אחרי הצלחה.
    """
    captcha_required.pop(username, None)
    captcha_tokens.pop(username, None)


def generate_captcha_token(username: str) -> str:
    """
    מייצר טוקן CAPTCHA עבור משתמש.
    """
    token = os.urandom(16).hex()
    captcha_tokens[username] = token
    return token


def verify_captcha_token(username: str, provided_token: str) -> bool:
    """
    בודק אם טוקן CAPTCHA תקף.
    """
    expected = captcha_tokens.get(username)
    return expected is not None and expected == provided_token


# ========================
#   עזר: attempts.log
# ========================
def log_attempt(username: str, result: str, latency_ms: float):
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "username": username,
        "hash_mode": HASH_MODE,
        "protections": PROTECTIONS_FLAGS,
        "result": result,
        "latency_ms": latency_ms,
        "group_seed": GROUP_SEED,
    }
    with open(ATTEMPTS_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# ========================
#   API endpoints
# ========================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/register", methods=["POST"])
def register():
    start = time.perf_counter()

    # מצפים ל-JSON בגוף
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        latency_ms = (time.perf_counter() - start) * 1000
        log_attempt(username or "", "fail_missing_fields", latency_ms)
        return jsonify({"error": "username and password required"}), 400

    users = load_users()

    if username in users:
        latency_ms = (time.perf_counter() - start) * 1000
        log_attempt(username, "fail_user_exists", latency_ms)
        return jsonify({"error": "user already exists"}), 400

    # יצירת salt אקראי
    salt = os.urandom(16).hex()
    password_hash = hash_password(password, salt, HASH_MODE)

    # totp_secret אקראי גם למשתמשים חדשים
    totp_secret = pyotp.random_base32()

    user_record = {
        "username": username,
        "password_hash": password_hash,
        "salt": salt,
        "password_strength": "unknown",  # נעדכן כשנבנה dataset
        "hash_mode": HASH_MODE,
        "totp_secret": totp_secret,
    }

    users[username] = user_record
    save_users(users)

    latency_ms = (time.perf_counter() - start) * 1000
    log_attempt(username, "register_success", latency_ms)
    return jsonify({"status": "ok"}), 201


@app.route("/login", methods=["POST"])
def login():
    start = time.perf_counter()

    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    captcha_token = data.get("captcha_token")

    # רישום בקשה ובדיקת rate limit
    register_request(username)
    if is_rate_limited(username):
        latency_ms = (time.perf_counter() - start) * 1000
        log_attempt(username or "", "fail_rate_limited", latency_ms)
        return jsonify({"error": "too many requests"}), 429

    if not username or not password:
        latency_ms = (time.perf_counter() - start) * 1000
        log_attempt(username or "", "fail_missing_fields", latency_ms)
        return jsonify({"error": "username and password required"}), 400

    # בדיקת CAPTCHA אם נדרש
    if check_captcha_required(username):
        if not captcha_token:
            latency_ms = (time.perf_counter() - start) * 1000
            log_attempt(username, "fail_captcha_required", latency_ms)
            return jsonify({"error": "captcha required", "captcha_required": True}), 403
        
        if not verify_captcha_token(username, captcha_token):
            latency_ms = (time.perf_counter() - start) * 1000
            log_attempt(username, "fail_captcha_invalid", latency_ms)
            return jsonify({"error": "invalid captcha token"}), 403

    users = load_users()
    user = users.get(username)

    if not user:
        latency_ms = (time.perf_counter() - start) * 1000
        # בכוונה לא אומרים אם המשתמש קיים או לא
        log_attempt(username, "fail_no_such_user", latency_ms)
        register_captcha_failure(username)
        return jsonify({"error": "invalid credentials"}), 401

    # בדיקת lockout
    if is_account_locked(username):
        latency_ms = (time.perf_counter() - start) * 1000
        log_attempt(username, "fail_locked_out", latency_ms)
        return jsonify({"error": "account locked"}), 403

    salt = user["salt"]
    stored_hash = user["password_hash"]
    user_hash_mode = user.get("hash_mode", HASH_MODE)

    if not verify_password(password, salt, user_hash_mode, stored_hash):
        register_failed_login(username)
        register_captcha_failure(username)
        latency_ms = (time.perf_counter() - start) * 1000
        log_attempt(username, "fail_bad_password", latency_ms)
        return jsonify({"error": "invalid credentials"}), 401

    # הצלחה – מאפסים מונה כישלונות
    reset_failed_logins(username)
    reset_captcha(username)

    latency_ms = (time.perf_counter() - start) * 1000
    log_attempt(username, "login_success", latency_ms)
    return jsonify({"status": "ok"}), 200


@app.route("/admin/get_captcha_token", methods=["GET"])
def get_captcha_token():
    """
    Admin endpoint to get a CAPTCHA token for automated testing.
    Requires valid GROUP_SEED for security.
    """
    provided_seed = request.args.get("group_seed")
    username = request.args.get("username")
    
    if not provided_seed or not username:
        return jsonify({"error": "group_seed and username required"}), 400
    
    try:
        provided_seed_int = int(provided_seed)
    except ValueError:
        return jsonify({"error": "invalid group_seed"}), 400
    
    if provided_seed_int != GROUP_SEED:
        return jsonify({"error": "unauthorized"}), 403
    
    token = generate_captcha_token(username)
    return jsonify({"captcha_token": token}), 200


@app.route("/login_totp", methods=["POST"])
def login_totp():
    """
    התחברות עם סיסמה + קוד TOTP
    מצפים ל-JSON:
    {
      "username": "...",
      "password": "...",
      "totp_code": "123456",
      "captcha_token": "..." (optional, if CAPTCHA required)
    }
    """
    start = time.perf_counter()

    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    totp_code = data.get("totp_code") or data.get("otp") or data.get("code")
    captcha_token = data.get("captcha_token")

    # רישום בקשה ובדיקת rate limit
    register_request(username)
    if is_rate_limited(username):
        latency_ms = (time.perf_counter() - start) * 1000
        log_attempt(username or "", "fail_rate_limited_totp", latency_ms)
        return jsonify({"error": "too many requests"}), 429

    if not username or not password or not totp_code:
        latency_ms = (time.perf_counter() - start) * 1000
        log_attempt(username or "", "fail_missing_fields_totp", latency_ms)
        return jsonify({"error": "username, password and totp_code required"}), 400

    # בדיקת CAPTCHA אם נדרש
    if check_captcha_required(username):
        if not captcha_token:
            latency_ms = (time.perf_counter() - start) * 1000
            log_attempt(username, "fail_captcha_required_totp", latency_ms)
            return jsonify({"error": "captcha required", "captcha_required": True}), 403
        
        if not verify_captcha_token(username, captcha_token):
            latency_ms = (time.perf_counter() - start) * 1000
            log_attempt(username, "fail_captcha_invalid_totp", latency_ms)
            return jsonify({"error": "invalid captcha token"}), 403

    users = load_users()
    user = users.get(username)

    if not user:
        latency_ms = (time.perf_counter() - start) * 1000
        log_attempt(username, "fail_no_such_user_totp", latency_ms)
        register_captcha_failure(username)
        return jsonify({"error": "invalid credentials"}), 401

    # בדיקת lockout
    if is_account_locked(username):
        latency_ms = (time.perf_counter() - start) * 1000
        log_attempt(username, "fail_locked_out_totp", latency_ms)
        return jsonify({"error": "account locked"}), 403

    # בדיקת סיסמה קודם
    salt = user["salt"]
    stored_hash = user["password_hash"]
    user_hash_mode = user.get("hash_mode", HASH_MODE)

    if not verify_password(password, salt, user_hash_mode, stored_hash):
        register_failed_login(username)
        register_captcha_failure(username)
        latency_ms = (time.perf_counter() - start) * 1000
        log_attempt(username, "fail_bad_password_totp", latency_ms)
        return jsonify({"error": "invalid credentials"}), 401

    # בדיקת TOTP
    secret = user.get("totp_secret")
    if not secret:
        latency_ms = (time.perf_counter() - start) * 1000
        log_attempt(username, "fail_no_totp_configured", latency_ms)
        return jsonify({"error": "totp not configured for this user"}), 400

    totp = pyotp.TOTP(secret)
    if not totp.verify(str(totp_code), valid_window=1):
        register_failed_login(username)
        register_captcha_failure(username)
        latency_ms = (time.perf_counter() - start) * 1000
        log_attempt(username, "fail_bad_totp", latency_ms)
        return jsonify({"error": "invalid credentials"}), 401

    # הצלחה – מאפסים מונה
    reset_failed_logins(username)
    reset_captcha(username)

    latency_ms = (time.perf_counter() - start) * 1000
    log_attempt(username, "login_totp_success", latency_ms)
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # debug=True רק לפיתוח
    app.run(debug=True)

