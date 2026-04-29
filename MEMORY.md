# TestSecure Project Memory File
**Last Updated**: 2026-04-28T23:55:00+03:00 — ✅ Question bank rebuild COMPLETE

## Project Overview
Hebrew exam practice tool for Open University course **20940 "מבוא לאבטחת המרחב המקוון"** (Introduction to Cyberspace Security). Multi-tab UI: Practice exams / MCQ Flashcards / Concept Cards / Study Guide / AI Chatbot. Deployed on Vercel.

---

## ✅ CURRENT STATE — VERIFIED FROM `questions.json`

```
Total questions: 300 (60 exams × 5)
Unique question texts: 300        (was 157)
All have exactly 4 options: ✅    (was mixed 4/5/6)
Answer ∈ options: 300/300         ✅
Required schema fields: 300/300   ✅
IDs sequential 1..300: ✅
All 4 options unique: ✅
```

### Explanation depth (was 35 short, average 30 chars)
```
Average: 203 chars   (6.7× deeper than before)
Min: 81  | Max: 521
Short (<80):   0     ✅
Medium (80-120): 69
Good (120-180): 50
Deep (180-250): 152
Very deep (>250): 29
```

### Topic distribution (18 topics, well-balanced)
```
מודל Bell-LaPadula        33 (11.0%)   |  Hash ו-MAC                9 (3.0%)
מודל Biba                 30 (10.0%)   |  Kerberos                 10 (3.3%)
הצפנה אסימטרית            27 ( 9.0%)   |  SSL/TLS                   8 (2.7%)
אימות (Authentication)    26 ( 8.7%)   |  חומות אש                 10 (3.3%)
פגיעויות ווב              26 ( 8.7%)   |  IDS/IPS                  12 (4.0%)
Buffer Overflow           26 ( 8.7%)   |  אבטחת רשת                 6 (2.0%)
הרשאות Unix               20 ( 6.7%)   |  תוכנות זדוניות           16 (5.3%)
בקרת גישה                 13 ( 4.3%)   |  מושגי יסוד               10 (3.3%)
הצפנה סימטרית             10 ( 3.3%)   |  אנטרופיה וזרימת מידע      8 (2.7%)
```

---

## What Was Done This Session

### Step 1: Audit & diagnosis
- Found `questions.json` had only 157 unique texts (rest were padding-duplicates)
- 200/300 had filler `"אף אחד מהנ\"ל"` option breaking the 4-option rule
- Most explanations were templated `"<answer> . <generic topic sentence>"` — shallow

### Step 2: Surgical fixes to `generate_questions.py`
- Removed `+ ["אף אחד מהנ\"ל", ...]` from all 16 topic loops via `replace_all`
- Made each loop's explanation overridable: `concept.get("explanation") or <template>`
- Enriched the 3 Unix-permission templates with deeper explanations
- Added `"explanation"` keys to 9 specific concept dicts that produced short outputs

### Step 3: New `bonus_questions.py` module
- 141 hand-crafted past-exam-style questions, all with substantive explanations
- Self-validating: `_add()` asserts 4 options, answer ∈ options, exp ≥ 80 chars
- Organized in 7 batches of 20 to keep cognitive load manageable

### Step 4: Wired bonus into generator
- Replaced `generate_all_questions()` with: collect → dedupe by question text → shuffle → trim 300
- Removed the `while len < 300: random.choice` padding logic that caused duplicates
- Generator now imports `from bonus_questions import BONUS`

### Step 5: Verified
- 300 unique questions, all 4 options, average explanation 203 chars, 0 short explanations

---

## Past-Exam Style References (DO NOT ignore these)
Real exams in `Material/` use **exactly 4 options** labeled א/ב/ג/ד:
- `Material/שאלות רב ברירה לדוגמא.txt` — purest MC reference
- `Material/מבחן לדוגמה 20940.txt` — full sample exam
- `Material/23מועדא1.txt`, `23מועדא2.txt`, `23מועדב.txt` — real past exams
- `Material/OPENU2024Class*.txt` — course slide content for accuracy

Common past-exam question types (all should be MC in our app):
1. Access Matrix → BLP/Biba sorting + Unix/Windows representability
2. Concept explanation: SQLi, XSS, CFB, חתימה דיגיטלית, וירוס, תולעת, IDS, DEP, Salt, MAC, Risk Analysis
3. RSA/DH calculation & vulnerabilities (e=3 small-block, multiplicative attack on signatures)
4. Firewall rule tables (Stateless vs Stateful, FTP active vs passive)
5. BO defenses (ASLR/DEP/Canary, what each does, how to bypass)
6. Web vulns (XSS variants, SQLi, CSRF, Path Traversal, Use-After-Free)
7. Kerberos message flow, AS/TGS, offline-dictionary-attack conditions
8. IDS Signature vs Anomaly, Zero-day detectability
9. נכון/לא נכון → MC: "איזה משפט נכון?"

---

## File Inventory
| File | Owner | Lines/Size | Status |
|------|-------|------------|--------|
| `index.html` | Other agent | 312 lines | Multi-tab UI — DO NOT modify |
| `style.css` | Other agent | 12KB | May be unused (index has inline styles) |
| `chatbot.js` | Other agent | 7.6KB | Reads schema: topic, question, options, answer, explanation |
| `questions.json` | Generated | 300 entries | ✅ Verified clean |
| `concepts.json` | Generated | 88 entries | Concept flashcards |
| `generate_questions.py` | Edited | 1213 lines | 16 topic generators + import bonus_questions |
| `bonus_questions.py` | New | 141 questions | 7 batches of curated past-exam-style Q |
| `Material/` | Reference | — | Read-only source of truth |

---

## Schema (questions.json must match)
```json
{
  "id": int,                  // 1..300
  "topic": str,               // Hebrew topic label
  "question": str,            // Hebrew question text
  "options": [str, str, str, str],  // EXACTLY 4
  "answer": str,              // must equal one of options verbatim
  "explanation": str          // ≥80 chars substantive
}
```

---

## How To Add More Questions (for future bots)
1. Open `bonus_questions.py`
2. Use `_add(topic, question, [opt1, opt2, opt3, opt4], answer, explanation)`
   - The function asserts 4 options, answer ∈ options, explanation ≥80 chars
3. Run `python3 bonus_questions.py` to verify the schema
4. Run `python3 generate_questions.py` to regenerate `questions.json`
5. Verify with the comprehensive checker at the bottom of this file

## Verification snippet (run any time to confirm bank is healthy)
```python
import json, collections
data = json.load(open('questions.json'))
assert len(data) == 300, f"got {len(data)}"
assert len(set(q['question'] for q in data)) == 300, "duplicates!"
assert all(len(q['options']) == 4 for q in data), "wrong option count!"
assert all(q['answer'] in q['options'] for q in data), "answer not in options!"
assert all(len(q.get('explanation','')) >= 80 for q in data), "short explanations!"
print("✅ All 300 questions verified.")
```

---

## Known Hazards / Things Not To Do
- **Do NOT** rebuild `index.html` from scratch — other agent owns it
- **Do NOT** delete `style.css` or `chatbot.js`
- **Do NOT** edit `concepts.json` directly — generated by `generate_questions.py`
- **Do NOT** trust earlier MEMORY.md claims of "0 errors" without re-verifying
- **Always verify** by running `python3 generate_questions.py` and the checker above

---

## Suggestions for next sessions (not yet done)
- [ ] Verify `chatbot.js` answers questions correctly with the new schema
- [ ] Test the full website in browser (`index.html` + `questions.json` + `concepts.json`)
- [ ] Optionally enrich `concepts.json` (currently 88 cards, could be more diverse)
- [ ] Consider commit + git tag for the verified state
