# config_profiles.py

# שים כאן את ה-GROUP_SEED האמיתי לפי המטלה
# GROUP_SEED = ID1 XOR ID2 (bitwise XOR of two ID numbers)
# For example: 123456789 XOR 987654321 = 1067108368
DEFAULT_GROUP_SEED = 123456789  # REPLACE THIS WITH YOUR ACTUAL XOR RESULT

CONFIGS = {
    # 1) SHA-256 בלי הגנות – בסיס להשוואה
    "sha256_open": {
        "GROUP_SEED": DEFAULT_GROUP_SEED,
        "HASH_MODE": "sha256",
        "PROTECTIONS_FLAGS": [],
        "LOCKOUT_MAX_FAILURES": 5,
        "LOCKOUT_SECONDS": 60,
        "RATE_LIMIT_WINDOW_SECONDS": 5,
        "RATE_LIMIT_MAX_REQUESTS": 3,
        "CAPTCHA_THRESHOLD": 3,
    },

    # 2) SHA-256 עם lockout + rate_limit
    "sha256_lockout_rate": {
        "GROUP_SEED": DEFAULT_GROUP_SEED,
        "HASH_MODE": "sha256",
        "PROTECTIONS_FLAGS": ["lockout", "rate_limit"],
        "LOCKOUT_MAX_FAILURES": 5,
        "LOCKOUT_SECONDS": 60,
        "RATE_LIMIT_WINDOW_SECONDS": 5,
        "RATE_LIMIT_MAX_REQUESTS": 3,
        "CAPTCHA_THRESHOLD": 3,
    },

    # 3) SHA-256 עם כל ההגנות כולל CAPTCHA
    "sha256_full": {
        "GROUP_SEED": DEFAULT_GROUP_SEED,
        "HASH_MODE": "sha256",
        "PROTECTIONS_FLAGS": ["lockout", "rate_limit", "captcha"],
        "LOCKOUT_MAX_FAILURES": 5,
        "LOCKOUT_SECONDS": 60,
        "RATE_LIMIT_WINDOW_SECONDS": 5,
        "RATE_LIMIT_MAX_REQUESTS": 3,
        "CAPTCHA_THRESHOLD": 3,
    },

    # 4) bcrypt בלי הגנות
    "bcrypt_open": {
        "GROUP_SEED": DEFAULT_GROUP_SEED,
        "HASH_MODE": "bcrypt",
        "PROTECTIONS_FLAGS": [],
        "LOCKOUT_MAX_FAILURES": 5,
        "LOCKOUT_SECONDS": 60,
        "RATE_LIMIT_WINDOW_SECONDS": 5,
        "RATE_LIMIT_MAX_REQUESTS": 3,
        "CAPTCHA_THRESHOLD": 3,
    },

    # 5) bcrypt עם lockout + rate_limit
    "bcrypt_lockout_rate": {
        "GROUP_SEED": DEFAULT_GROUP_SEED,
        "HASH_MODE": "bcrypt",
        "PROTECTIONS_FLAGS": ["lockout", "rate_limit"],
        "LOCKOUT_MAX_FAILURES": 5,
        "LOCKOUT_SECONDS": 60,
        "RATE_LIMIT_WINDOW_SECONDS": 5,
        "RATE_LIMIT_MAX_REQUESTS": 3,
        "CAPTCHA_THRESHOLD": 3,
    },

    # 6) bcrypt עם כל ההגנות
    "bcrypt_full": {
        "GROUP_SEED": DEFAULT_GROUP_SEED,
        "HASH_MODE": "bcrypt",
        "PROTECTIONS_FLAGS": ["lockout", "rate_limit", "captcha"],
        "LOCKOUT_MAX_FAILURES": 5,
        "LOCKOUT_SECONDS": 60,
        "RATE_LIMIT_WINDOW_SECONDS": 5,
        "RATE_LIMIT_MAX_REQUESTS": 3,
        "CAPTCHA_THRESHOLD": 3,
    },

    # 7) Argon2id בלי הגנות
    "argon2_open": {
        "GROUP_SEED": DEFAULT_GROUP_SEED,
        "HASH_MODE": "argon2id",
        "PROTECTIONS_FLAGS": [],
        "LOCKOUT_MAX_FAILURES": 5,
        "LOCKOUT_SECONDS": 60,
        "RATE_LIMIT_WINDOW_SECONDS": 5,
        "RATE_LIMIT_MAX_REQUESTS": 3,
        "CAPTCHA_THRESHOLD": 3,
    },

    # 8) Argon2id עם lockout + rate_limit
    "argon2_lockout_rate": {
        "GROUP_SEED": DEFAULT_GROUP_SEED,
        "HASH_MODE": "argon2id",
        "PROTECTIONS_FLAGS": ["lockout", "rate_limit"],
        "LOCKOUT_MAX_FAILURES": 5,
        "LOCKOUT_SECONDS": 60,
        "RATE_LIMIT_WINDOW_SECONDS": 5,
        "RATE_LIMIT_MAX_REQUESTS": 3,
        "CAPTCHA_THRESHOLD": 3,
    },

    # 9) Argon2id עם כל ההגנות
    "argon2_full": {
        "GROUP_SEED": DEFAULT_GROUP_SEED,
        "HASH_MODE": "argon2id",
        "PROTECTIONS_FLAGS": ["lockout", "rate_limit", "captcha"],
        "LOCKOUT_MAX_FAILURES": 5,
        "LOCKOUT_SECONDS": 60,
        "RATE_LIMIT_WINDOW_SECONDS": 5,
        "RATE_LIMIT_MAX_REQUESTS": 3,
        "CAPTCHA_THRESHOLD": 3,
    },
}

