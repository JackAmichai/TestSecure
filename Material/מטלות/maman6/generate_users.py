import os
import json

import pyotp

from config import DATA_DIR, USERS_FILE, HASH_MODE, GROUP_SEED
from app import hash_password  # משתמש בפונקציה שהגדרנו ב-app.py

USERS_PATH = os.path.join(DATA_DIR, USERS_FILE)


def get_password_sets():
    """
    מחזיר מילון עם שלוש רשימות סיסמאות:
    weak / medium / strong
    הסיסמאות נוצרו מראש בפייתון עם random.
    """
    weak_passwords = [
        str(GROUP_SEED),  # First password MUST be GROUP_SEED as per assignment
        "70336321",
        "8325861",
        "114659",
        "69536627",
        "jfqjemw",
        "232096",
        "zlsdzls",
        "96239796",
        "mdhquix",
    ]

    medium_passwords = [
        "yy93n52s",
        "pf48s5ypp",
        "8xz0wp27t",
        "3zq2fnnz8t",
        "vrerigml",
        "pqlui0dp4p",
        "dvjmido3",
        "i9lz9zmi",
        "xoh1iah8sb",
        "1z81eya3ow",
    ]

    strong_passwords = [
        "*KjtkMh3p_VbG",
        "c9u_3v#!KCyHJ!",
        "4uOL$2-V3x#fkl",
        "1r4AVQ_*ta!mlq",
        "5CowN#^eEgJc",
        "m2i0f3VCfl$RP",
        "!bhbLHut2#BJw",
        "9WuWdCjKxH7Yw!",
        "-o6A2^&nJFq_",
        "5YnP*%^^gTzVu1",
    ]

    return {
        "weak": weak_passwords,
        "medium": medium_passwords,
        "strong": strong_passwords,
    }


def generate_users():
    os.makedirs(DATA_DIR, exist_ok=True)

    password_sets = get_password_sets()
    users = []

    # לכל קטגוריה נדאג ל-usernames מסודרים
    for strength, pw_list in password_sets.items():
        for i, plain_pw in enumerate(pw_list, start=1):
            username = f"{strength}_user_{i:02d}"

            # salt אקראי לכל משתמש
            salt = os.urandom(16).hex()

            # hash לפי HASH_MODE הנוכחי (sha256 / bcrypt / argon2id)
            password_hash = hash_password(plain_pw, salt, HASH_MODE)

            # totp_secret אקראי לכל משתמש
            totp_secret = pyotp.random_base32()

            user_record = {
                "username": username,
                "password_hash": password_hash,
                "salt": salt,
                "password_strength": strength,  # weak / medium / strong
                "hash_mode": HASH_MODE,
                "totp_secret": totp_secret,
            }

            users.append(user_record)

    # כותבים את כל המשתמשים לקובץ JSON (רשימה)
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(users)} users into {USERS_PATH}")
    print(f"All users hashed with mode: {HASH_MODE}")
    print(f"GROUP_SEED: {GROUP_SEED}")
    print(f"Note: weak_user_01 password is GROUP_SEED ({GROUP_SEED})")


if __name__ == "__main__":
    generate_users()

