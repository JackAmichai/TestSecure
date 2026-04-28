# TestSecure Project Memory File
**Last Updated**: 2026-04-28T23:10:00+03:00 (mid-session: 3/7 bonus batches done = 60 Q)

## Project Overview
Hebrew exam practice tool for Open University course **20940 "מבוא לאבטחת המרחב המקוון"** (Introduction to Cyberspace Security). Multi-tab UI: Practice exams / MCQ Flashcards / Concept Cards / Study Guide / AI Chatbot. Deployed on Vercel.

---

## ⚠️ CURRENT TRUTHFUL STATE (verified by inspecting questions.json directly)

**DO NOT trust earlier MEMORY claims of "0 errors / completed" — they were aspirational.**

After running `python3 generate_questions.py` with current code:
- ✅ **300 questions** total (60 exams × 5)
- ✅ **All 4 options** per question (after the filler-removal fix)
- ✅ Per-question `explanation` field is now overridable (added `concept.get("explanation") or <template>` in 16 loop locations)
- ❌ **Only 164 unique question texts** out of 300 — the rest are duplicates from the `while len < 300: random.choice` padding logic at the end of `generate_all_questions`
- ❌ **35 explanations are still <80 chars** because most concept dicts don't have explicit `"explanation": "..."` keys yet — they fall back to the templated `"<answer> . <one_generic_topic_sentence>"`

### Topic distribution after re-run:
```
מודל Biba: 54           ← over-represented (random gen produces 25 + duplicates fill rest)
מודל Bell-LaPadula: 54  ← over-represented (same reason)
הרשאות Unix: 29
Hash ו-MAC: 18
הצפנה סימטרית: 16
Buffer Overflow: 15
תוכנות זדוניות: 15
בקרת גישה: 14
הצפנה אסימטרית: 13
אנטרופיה וזרימת מידע: 11
אימות (Authentication): 11
Kerberos: 10
פגיעויות ווב: 10
SSL/TLS: 10
חומות אש (Firewalls): 10
IDS/IPS: 10
```
The under-represented topics need padding via the BONUS module described below.

---

## Past-Exam Style (verified from `Material/`)
Real exams use **exactly 4 options** labeled א/ב/ג/ד. Reference files:
- `Material/שאלות רב ברירה לדוגמא.txt` — purest MC reference
- `Material/מבחן לדוגמה 20940.txt` — full sample exam (MC + open)
- `Material/23מועדא1.txt`, `23מועדא2.txt`, `23מועדב.txt` — real past exams
- `Material/OPENU2024Class*.txt` — course slide content for accuracy
- `Material/שאלות מקורס אבטחת מערכות תוכנה עם פתרונות.txt` — solved questions

Common past-exam question types (all should be MC in our app):
1. Access Matrix → BLP/Biba sorting + Unix/Windows representability
2. Concept explanation: SQLi, XSS, CFB, חתימה דיגיטלית, וירוס, תולעת, IDS, DEP, Salt, MAC, Risk Analysis
3. RSA / DH calculation & vulnerabilities (e=3 small-block attack, multiplicative attack on signatures)
4. Firewall rule tables (Stateless vs Stateful)
5. BO defenses (ASLR/DEP/Canary, what each does, how to bypass)
6. Web vulns (XSS variants, SQLi, CSRF, Directory Traversal, Use-After-Free)
7. Kerberos message flow, AS/TGS, offline-dictionary-attack conditions
8. IDS Signature vs Anomaly, Zero-day detectability, NIDS vs HIDS
9. נכון/לא נכון (true/false) — convert to MC: "איזה משפט נכון?"

---

## File Inventory (DO NOT delete without reason)
| File | Owner | Notes |
|------|-------|-------|
| `index.html` (43KB) | Other agent | Multi-tab UI, inline CSS+JS. **Do not modify.** |
| `style.css` (12KB) | Other agent | Premium dark-mode design — may be unused. |
| `chatbot.js` (7.6KB) | Other agent | Reads `questions.json` schema: `topic`, `question`, `options`, `answer`, `explanation` |
| `questions.json` (~240KB) | Generated | 300 entries — REGENERATED FROM `generate_questions.py` |
| `concepts.json` (~27KB) | Generated | 88 concept flashcards |
| `generate_questions.py` (1189 lines) | This bot's edits | 16 topic functions; needs bonus module to fix duplicates |
| `bonus_questions.py` | This bot (in progress) | NEW — holds 140 high-quality past-exam-style questions |
| `Material/` | Reference only | Read-only source of truth |

---

## Schema (questions.json must match)
```json
{
  "id": int,                  // 1..300
  "topic": str,               // Hebrew topic label
  "question": str,            // Hebrew question text
  "options": [str, str, str, str],  // EXACTLY 4
  "answer": str,              // must equal one of options
  "explanation": str          // 80+ chars substantive
}
```

---

## Plan In Progress (if you resume mid-session)

### Done so far this session
1. ✅ Surveyed Material/ — confirmed past-exam style is 4-option MC
2. ✅ Read previous MEMORY.md and audited actual questions.json (caught the dupes)
3. ✅ Removed `+ ["אף אחד מהנ\"ל"]` filler from all 16 loops → all questions now have exactly 4 options
4. ✅ Made each loop's explanation overridable: `concept.get("explanation") or <template>`

### Remaining: Build BONUS questions in 20-question batches
Plan to add **140 new high-quality questions** across topics that are currently under-represented OR repeated. Will be in a new `bonus_questions.py` module imported by `generate_questions.py`.

**Batches** (each = 20 Q, separate file write to keep cognitive load manageable):
| # | Topic Bundle | Target Count |
|---|------|------|
| 1 | אימות (Authentication) — passwords, salt, MFA, biometrics, SIM swap, FIDO2, replay, dictionary | 20 |
| 2 | פגיעויות ווב — XSS Stored/Reflected/DOM, SQLi (incl. Blind), CSRF, SSRF, Path Traversal, Cookies (HttpOnly/Secure/SameSite) | 20 |
| 3 | Buffer Overflow + פגיעויות תוכנה — Stack BO, ROP, Use-After-Free, Format String, Integer Overflow, ASLR bypass, Heap Spraying | 20 |
| 4 | הצפנה אסימטרית — RSA (e=3 attack, multiplicative attack), Digital Signatures, DH, MITM, Forward Secrecy, hybrid encryption | 20 |
| 5 | אבטחת רשת — Firewalls (FTP active/passive), IDS/IPS (Honeypot, Sig vs Anomaly Zero-day), IPSec (AH/ESP, NAT issues), TLS handshake, Kerberos message flow + offline dict attack | 20 |
| 6 | תוכנות זדוניות + מושגי יסוד + הנדסה חברתית — virus/worm/trojan/rootkit/ransomware, CIA triad, vulnerability vs threat, phishing/spear/whaling, defense-in-depth, zero-trust | 20 |
| 7 | BLP/Biba scenarios + בקרת גישה + Unix specific — covert channels, ערוץ נסתר via quota, high-water-mark, ACL vs C-list, SUID gotchas, directory x-bit | 20 |
| **Total** | | **140** |

After all 7 batches written, the wiring step:
- Modify `generate_questions.py` `generate_all_questions()`:
  * Import bonus questions
  * Build a `seen` set of question texts; **dedupe** before final list
  * Reduce BLP random gen from 25 → 8, Biba from 25 → 8 (since bonus adds curated ones)
  * **Remove the `while len < 300: random.choice(...)` padding** at lines ~1083-1085
  * Trim to first 300 unique
- Run, verify: 300 unique, all 4 options, all explanations ≥80 chars

---

## Known Hazards / Things Not To Do
- **Do NOT** rebuild index.html from scratch — other agent owns it and is iterating fast (last seen commit 9b68e62: AI Chatbot integration)
- **Do NOT** delete `style.css` or `chatbot.js` — used by index.html
- **Do NOT** edit `concepts.json` directly — it's generated by `generate_questions.py`
- **Do NOT** trust git status as the only source of truth — files get rewritten between sessions
- **Always verify** by running `python3 generate_questions.py && python3 -c "..."` to count actual unique questions

---

## How To Resume Mid-Session
1. `cd /Volumes/AI_Drive/Code/TestSecure`
2. Read this MEMORY.md
3. Check `git log --oneline -10` for any new commits
4. Check current state: `python3 -c "import json; data=json.load(open('questions.json')); print('unique:', len(set(q['question'] for q in data)))"` — should approach 300
5. If `bonus_questions.py` exists, count `BONUS = [...]` entries to know which batch you're in
6. Continue the next batch in the table above

---

## Update Cadence
This file is updated every ~5 min during active work. If timestamp is stale by >30 min, the bot probably crashed mid-batch — pick up from the next pending batch in the plan.
