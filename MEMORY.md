# TestSecure Project Memory File
**Last Updated**: 2026-04-28T17:40:00+03:00

## Project Overview
Hebrew exam practice tool for Open University course 20940 "מבוא לאבטחת המרחב המקוון".

## COMPLETED WORK
### ✅ Questions Fixed (2026-04-28)
- Generated 300 high-quality MCQ questions across 17 topics
- 0 answer errors (all answers in options)
- 60 exams × 5 questions each
- Detailed Hebrew explanations for every question
- All BLP/Biba logic verified correct
- Saved to questions.json

### ✅ Concepts Fixed (2026-04-28)
- Generated 45 quality concept flashcards
- Mix of "הגדר מושג" and "נכון/לא נכון"
- Saved to concepts.json

### Topic Distribution (300 questions):
- מודל Bell-LaPadula: 28
- הרשאות Unix: 28
- מודל Biba: 23
- הצפנה סימטרית: 19
- פגיעויות ווב: 19
- תוכנות זדוניות: 19
- בקרת גישה: 17
- Hash ואימות: 17
- הצפנה אסימטרית: 16
- SSL/TLS: 16
- חומות אש: 16
- Buffer Overflow: 16
- חתימה דיגיטלית ו-PKI: 14
- Kerberos: 14
- IDS/IPS: 13
- אימות זהות: 13
- אנטרופיה וזרימת מידע: 12

## STILL TODO
- [ ] Update index.html to use the premium dark-mode style.css (currently has inline styles)
- [ ] The style.css has a full premium design system but index.html doesn't link to it
- [ ] Update index.html JS to handle 300 questions / 60 exams properly
- [ ] Clean up temp files (q_part*.py, q_part*.json) - DONE

## Architecture
- `index.html` - Main app (needs style.css integration)
- `style.css` - Premium dark-mode design (NOT linked yet!)
- `questions.json` - 300 MCQ questions ✅
- `concepts.json` - 45 concept flashcards ✅
- `generate_questions.py` - Old generator (can be deleted)
- `Material/` - Reference exam papers
