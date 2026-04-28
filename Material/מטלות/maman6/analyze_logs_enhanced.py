import os
import json
import datetime
import statistics
from collections import defaultdict, Counter

from config import DATA_DIR, LOGS_DIR, USERS_FILE, ATTEMPTS_LOG_FILE

USERS_PATH = os.path.join(DATA_DIR, USERS_FILE)
ATTEMPTS_LOG_PATH = os.path.join(LOGS_DIR, ATTEMPTS_LOG_FILE)


def load_users():
    """טוען users.json ומחזיר מילון username -> user_info"""
    if not os.path.exists(USERS_PATH):
        print(f"Users file not found: {USERS_PATH}")
        return {}

    with open(USERS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    users = {}
    for u in data:
        users[u["username"]] = u
    return users


def load_attempts():
    """טוען את attempts.log כ-list של dicts"""
    attempts = []
    if not os.path.exists(ATTEMPTS_LOG_PATH):
        print(f"Attempts log not found: {ATTEMPTS_LOG_PATH}")
        return attempts

    with open(ATTEMPTS_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                attempts.append(rec)
            except json.JSONDecodeError:
                continue

    return attempts


def parse_timestamp(ts: str) -> datetime.datetime:
    """מתרגם ISO timestamp ל- datetime"""
    # מורידים Z בסוף אם צריך
    if ts.endswith("Z"):
        ts = ts[:-1]
    return datetime.datetime.fromisoformat(ts)


def calculate_percentile(values, percentile):
    """חישוב percentile מרשימת ערכים"""
    if not values:
        return 0
    sorted_values = sorted(values)
    k = (len(sorted_values) - 1) * percentile / 100
    f = int(k)
    c = k - f
    if f + 1 < len(sorted_values):
        return sorted_values[f] + c * (sorted_values[f + 1] - sorted_values[f])
    else:
        return sorted_values[f]


def analyze_comprehensive():
    """
    ניתוח מקיף של הלוגים עם סטטיסטיקות מתקדמות.
    """
    users = load_users()
    attempts = load_attempts()

    if not attempts:
        print("No attempts to analyze.")
        return

    # הוסף password_strength לכל attempt
    for a in attempts:
        uname = a.get("username")
        uinfo = users.get(uname)
        if uinfo:
            a["password_strength"] = uinfo.get("password_strength", "unknown")
        else:
            a["password_strength"] = "unknown"

    # קבץ לפי (hash_mode, protections, password_strength)
    groups = defaultdict(list)
    for a in attempts:
        hash_mode = a.get("hash_mode", "unknown")
        protections = tuple(sorted(a.get("protections", [])))
        strength = a.get("password_strength", "unknown")
        key = (hash_mode, protections, strength)
        groups[key].append(a)

    print("\n" + "="*80)
    print("COMPREHENSIVE LOG ANALYSIS")
    print("="*80 + "\n")

    all_stats = []

    for key, recs in sorted(groups.items()):
        hash_mode, protections, strength = key
        
        print("-" * 80)
        print(f"Configuration:")
        print(f"  Hash Mode:         {hash_mode}")
        print(f"  Protections:       {list(protections) if protections else 'None'}")
        print(f"  Password Strength: {strength}")
        print("-" * 80)

        # סה"כ ניסיונות
        total_attempts = len(recs)

        # ספירת תוצאות
        results_counter = Counter(r["result"] for r in recs)
        
        # הצלחות
        successes = [r for r in recs if "success" in r["result"]]
        success_count = len(successes)
        success_rate = (success_count / total_attempts * 100) if total_attempts > 0 else 0

        # זמנים
        timestamps = [parse_timestamp(r["timestamp"]) for r in recs]
        t_min = min(timestamps)
        t_max = max(timestamps)
        total_duration = (t_max - t_min).total_seconds()
        
        attempts_per_sec = total_attempts / total_duration if total_duration > 0 else float("inf")

        # Latency statistics
        latencies = [r.get("latency_ms", 0.0) for r in recs]
        avg_latency = statistics.mean(latencies) if latencies else 0
        median_latency = statistics.median(latencies) if latencies else 0
        
        # Percentiles
        p50 = calculate_percentile(latencies, 50)
        p90 = calculate_percentile(latencies, 90)
        p95 = calculate_percentile(latencies, 95)
        p99 = calculate_percentile(latencies, 99)

        # Time to first success
        time_to_first_success = None
        if successes:
            first_success_time = min(parse_timestamp(s["timestamp"]) for s in successes)
            time_to_first_success = (first_success_time - t_min).total_seconds()

        # Failed attempts analysis
        failures = [r for r in recs if "fail" in r["result"] or "invalid" in r.get("error", "")]
        lockout_count = sum(1 for r in recs if "locked" in r["result"])
        rate_limit_count = sum(1 for r in recs if "rate_limit" in r["result"])
        captcha_count = sum(1 for r in recs if "captcha" in r["result"])

        # Print statistics
        print(f"\nGeneral Statistics:")
        print(f"  Total attempts:              {total_attempts}")
        print(f"  Duration:                    {total_duration:.2f} seconds")
        print(f"  Attempts per second:         {attempts_per_sec:.2f}")
        
        print(f"\nSuccess Statistics:")
        print(f"  Successful attempts:         {success_count}")
        print(f"  Success rate:                {success_rate:.2f}%")
        if time_to_first_success is not None:
            print(f"  Time to first success:       {time_to_first_success:.2f} seconds")
        else:
            print(f"  Time to first success:       N/A (no successes)")

        print(f"\nLatency Statistics (ms):")
        print(f"  Average:                     {avg_latency:.2f}")
        print(f"  Median:                      {median_latency:.2f}")
        print(f"  50th percentile (P50):       {p50:.2f}")
        print(f"  90th percentile (P90):       {p90:.2f}")
        print(f"  95th percentile (P95):       {p95:.2f}")
        print(f"  99th percentile (P99):       {p99:.2f}")

        print(f"\nProtection Events:")
        print(f"  Lockout events:              {lockout_count}")
        print(f"  Rate limit events:           {rate_limit_count}")
        print(f"  CAPTCHA challenges:          {captcha_count}")

        print(f"\nResults Breakdown:")
        for result, count in results_counter.most_common():
            percentage = (count / total_attempts * 100) if total_attempts > 0 else 0
            print(f"  {result:30s} {count:6d} ({percentage:5.1f}%)")

        # Extrapolation for incomplete attacks
        if success_count == 0 and total_attempts > 0:
            print(f"\nExtrapolation (No success achieved):")
            print(f"  Note: Attack did not succeed in {total_attempts} attempts.")
            if strength == "weak":
                # Estimate based on typical weak password space
                estimated_keyspace = 10000  # Typical for 4-digit pins or simple passwords
                estimated_time = (estimated_keyspace / attempts_per_sec) if attempts_per_sec > 0 else float("inf")
                print(f"  Estimated keyspace (weak):   ~{estimated_keyspace:,}")
                print(f"  Estimated time to exhaust:   {estimated_time:.2f} seconds ({estimated_time/3600:.2f} hours)")
            elif strength == "medium":
                estimated_keyspace = 10**8  # 100 million combinations
                estimated_time = (estimated_keyspace / attempts_per_sec) if attempts_per_sec > 0 else float("inf")
                print(f"  Estimated keyspace (medium): ~{estimated_keyspace:,}")
                print(f"  Estimated time to exhaust:   {estimated_time:.2f} seconds ({estimated_time/86400:.2f} days)")
            elif strength == "strong":
                estimated_keyspace = 10**12  # 1 trillion combinations
                estimated_time = (estimated_keyspace / attempts_per_sec) if attempts_per_sec > 0 else float("inf")
                print(f"  Estimated keyspace (strong): ~{estimated_keyspace:,}")
                print(f"  Estimated time to exhaust:   {estimated_time:.2f} seconds ({estimated_time/31536000:.2f} years)")

        print()

        # Store stats for summary table
        all_stats.append({
            "hash_mode": hash_mode,
            "protections": list(protections),
            "strength": strength,
            "total_attempts": total_attempts,
            "success_count": success_count,
            "success_rate": success_rate,
            "duration": total_duration,
            "attempts_per_sec": attempts_per_sec,
            "avg_latency": avg_latency,
            "median_latency": median_latency,
            "time_to_first_success": time_to_first_success,
            "lockout_count": lockout_count,
            "rate_limit_count": rate_limit_count,
            "captcha_count": captcha_count,
        })

    # Summary table
    print("="*80)
    print("SUMMARY TABLE")
    print("="*80)
    print(f"{'Hash':<10} {'Protections':<30} {'Strength':<8} {'Attempts':>8} {'Success':>7} {'Rate':>6} {'Time(s)':>8}")
    print("-"*80)
    
    for stat in all_stats:
        protections_str = ",".join(stat["protections"]) if stat["protections"] else "none"
        print(f"{stat['hash_mode']:<10} {protections_str:<30} {stat['strength']:<8} "
              f"{stat['total_attempts']:>8} {stat['success_count']:>7} {stat['success_rate']:>5.1f}% "
              f"{stat['duration']:>8.1f}")

    print("="*80)

    # Save statistics to JSON
    stats_file = os.path.join(LOGS_DIR, "analysis_summary.json")
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(all_stats, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed statistics saved to: {stats_file}")
    print()


if __name__ == "__main__":
    analyze_comprehensive()
