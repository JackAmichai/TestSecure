# TestSecure Project Memory File
**Last Updated**: 2026-04-28T20:05:00+03:00 (current session: Q-rebuild for past-exam style)

## Project Overview
Hebrew exam practice tool for Open University course 20940 "מבוא לאבטחת המרחב המקוון". Deployed on Vercel.

## Where Previous Sessions Stopped
- 300 questions, 60 exams, AI chatbot integrated, dark-mode UI
- ~16 topics covered

## Issues Found in Current Session (2026-04-28 20:00)
After analyzing questions.json carefully, found serious quality problems:

1. **Duplicate questions**: only 157 unique question texts out of 300 (47% duplicates)
2. **Inconsistent options**: 100 q have 4 options, 182 have 5, 18 have 6 — past exams use exactly 4
3. **"אף אחד מהנ\"ל" filler in 200/300**: not in style of past exams (Maamad א/ב 2023, "שאלות רב ברירה לדוגמא")
4. **Shallow explanations**: most are just "<answer> . <generic topic sentence>"
5. **Topic skew**: Biba 55 + BLP 47 = 102 (34%) — too heavy, while Authentication=8, Malware=9 underweight
6. **Auto-generated BLP/Biba**: random subject/object/level permutations — lack the scenario depth of past exams

## Past-Exam Style (verified from Material/)
- Real exam files: 23מועדא1.txt, 23מועדא2.txt, 23מועדב.txt, מבחן לדוגמה 20940.txt
- MC reference: שאלות רב ברירה לדוגמא.txt has exactly 4 options labeled א/ב/ג/ד
- Common question types in past exams:
  * Access Matrix scenarios (BLP/Biba sorting)
  * True/False with brief justification (we convert to MC: "which statement is correct?")
  * Concept explanations (we convert to MC: "what is X?")
  * RSA/DH calculations & vulnerabilities (e=3 issue, multiplicative attack)
  * Firewall rules table (stateless/stateful)
  * Buffer Overflow defenses (ASLR/DEP/Canary, what each does, how to bypass)
  * Web vulns (XSS, SQLi, CSRF, Directory Traversal, Use-After-Free)
  * Kerberos message flow & offline dictionary attack
  * IDS signatures vs anomaly, Zero-day detectability

## Plan for Current Session
1. ✅ Survey Material/ folder — done
2. ✅ Read MEMORY.md and check current state — done
3. 🔄 Rewrite question bank: 300 unique, 4-option, real-style questions covering all curriculum topics
4. 🔄 Each q: substantive explanation referring to course material/exam tradition
5. 🔄 Better topic distribution (target ~20 per major topic, ~10-15 per minor)
6. 🔄 Update generate_questions.py to be a static curated bank (not generative)
7. 🔄 Regenerate questions.json with new bank
8. 🔄 Verify answer correctness, schema match, exact 4 options each
9. 🔄 Don't touch index.html (other agent owns the UI), but match its schema

## Target Topic Distribution (rebalanced)
| Topic | Target | Notes |
|-------|--------|-------|
| מודל Bell-LaPadula | 20 | Confidentiality, no-read-up, no-write-down, scenarios |
| מודל Biba | 18 | Integrity, no-read-down, no-write-up |
| בקרת גישה DAC/MAC/RBAC | 18 | Access matrix, ACL, C-list, models |
| הרשאות Unix/Windows | 18 | UGO, SUID, SetGID, Sticky, ACL, DACL/SACL |
| ערוץ נסתר ואנטרופיה | 12 | Covert channels, info-leak bits |
| הצפנה סימטרית | 18 | AES, DES, 3DES, modes (CBC, ECB, CFB, OFB, CTR), IV |
| הצפנה אסימטרית | 22 | RSA, e=3 attack, signatures, multiplicative attack |
| Hash, MAC, חתימה | 20 | SHA, collision, birthday, HMAC, replay |
| Diffie-Hellman / החלפת מפתחות | 12 | DH, MITM, Forward Secrecy |
| אימות (סיסמאות, MFA, ביומטריה) | 22 | Password attacks, salt, MFA, biometrics, SIM swap |
| Kerberos | 14 | AS, TGS, tickets, offline dict attack, Realm |
| Buffer Overflow ופגיעויות תוכנה | 22 | Stack BO, ASLR, DEP, Canary, ROP, UAF, Format String |
| פגיעויות ווב (XSS/SQLi/CSRF) | 20 | XSS variants, SQLi, CSRF, SSRF, Path Traversal, Cookies |
| חומות אש (Firewalls) | 14 | Stateless/Stateful/Proxy, Rules, FTP active/passive |
| IDS/IPS | 12 | Sig vs anomaly, NIDS/HIDS, Zero-day, Honeypot |
| SSL/TLS | 12 | Handshake, cipher suite, FS, certs |
| IPSec / VPN | 10 | AH/ESP, Transport/Tunnel, NAT issues, IKE |
| תוכנות זדוניות | 16 | Virus/Worm/Trojan/Rootkit/Ransomware/Spyware/Bot/Logic Bomb |
| התקפות רשת | 10 | DoS/DDoS, SYN flood, Reflection, Sniffing, ARP/DNS poisoning, IP spoofing |
| מושגי יסוד (CIA, איום/פגיעות/נכס) | 10 | Vulnerability vs threat, CIA triad, defense in depth, social engineering |
| **Total** | **300** | exactly 60 exams of 5 |

## Architecture (do NOT modify)
- `index.html` (43KB) - Other agent's multi-tab UI: Practice / Cards / Guide / AI Chatbot
- `style.css` (12KB) - Premium design (might be unused since index has inline styles)
- `concepts.json` (27KB, 45 entries) - Concept flashcards — keep as-is
- `Material/` - Reference materials (read-only)
- Schema for questions.json: `{id, topic, question, options[4], answer, explanation}`

## Schedule for Memory Updates
Update this file every ~5 minutes during work to make session resumable.
