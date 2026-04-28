import os
import json
import datetime
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


def analyze():
    users = load_users()
    attempts = load_attempts()

    if not attempts:
        print("No attempts to analyze.")
        return

    # נוסיף לכל Attempt את password_strength
    for a in attempts:
        uname = a.get("username")
        uinfo = users.get(uname)
        if uinfo:
            a["password_strength"] = uinfo.get("password_strength", "unknown")
        else:
            a["password_strength"] = "unknown"

    # נאגד לפי (hash_mode, tuple(protections), password_strength)
    groups = defaultdict(list)
    for a in attempts:
        hash_mode = a.get("hash_mode", "unknown")
        protections = tuple(a.get("protections", []))
        strength = a.get("password_strength", "unknown")
        key = (hash_mode, protections, strength)
        groups[key].append(a)

    print("\n=== Summary by hash_mode / protections / password_strength ===\n")

    for key, recs in groups.items():
        hash_mode, protections, strength = key
        results_counter = Counter(r["result"] for r in recs)

        # חישוב attempts/sec לפי טווח זמנים בין ניסיון ראשון לאחרון
        timestamps = [parse_timestamp(r["timestamp"]) for r in recs]
        t_min = min(timestamps)
        t_max = max(timestamps)
        delta = (t_max - t_min).total_seconds()
        total_attempts = len(recs)
        attempts_per_sec = total_attempts / delta if delta > 0 else float("inf")

        avg_latency = sum(r.get("latency_ms", 0.0) for r in recs) / total_attempts

        print("-----------------------------------------------------")
        print(f"hash_mode:         {hash_mode}")
        print(f"protections:       {list(protections)}")
        print(f"password_strength: {strength}")
        print(f"total_attempts:    {total_attempts}")
        print(f"attempts/sec:      {attempts_per_sec:.2f}")
        print(f"avg_latency_ms:    {avg_latency:.2f}")
        print("results breakdown:")
        for res, count in results_counter.items():
            print(f"  {res:25s} {count}")
        print()

    print("=== End of summary ===")


if __name__ == "__main__":
    analyze()

