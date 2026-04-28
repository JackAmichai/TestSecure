
import json
import random

def generate_mcqs(count):
    questions = []
    subjects = ["אליס", "בוב", "משתמש א'", "משתמש ב'", "המנהל", "התוקף", "איב"]
    objects = ["קובץ סודי", "תיקייה משותפת", "מסד נתונים", "קוד המקור", "יומן המערכת"]
    levels = ["Top Secret", "Secret", "Confidential", "Unclassified"]
    integ_levels = ["High", "Medium", "Low"]

    for i in range(count):
        # Choose template type
        r = random.random()
        if r < 0.25: # BLP
            s, o = random.choice(subjects), random.choice(objects)
            l1, l2 = random.choice(levels), random.choice(levels)
            q_text = f"במודל BLP, האם {s} (סיווג {l1}) יכול לקרוא את {o} (סיווג {l2})?"
            ans = "כן" if levels.index(l1) <= levels.index(l2) else "לא"
            opts = ["כן", "לא", "רק עם הרשאת ROOT", "תלוי ב-ACL"]
            topic = "מודל Bell-LaPadula"
            exp = "לפי כלל ה-Simple Security (No Read Up), סובייקט יכול לקרוא רק אובייקט ברמה שלו או נמוכה ממנה."
        elif r < 0.5: # Biba
            s, o = random.choice(subjects), random.choice(objects)
            i1, i2 = random.choice(integ_levels), random.choice(integ_levels)
            q_text = f"במודל Biba, האם {s} (רמת שלמות {i1}) יכול לכתוב ל-{o} (רמת שלמות {i2})?"
            ans = "כן" if integ_levels.index(i1) <= integ_levels.index(i2) else "לא"
            opts = ["כן", "לא", "רק אם הוא הבעלים", "לא מוגדר במודל"]
            topic = "מודל Biba"
            exp = "לפי כלל ה-*-Integrity (No Write Up), סובייקט לא יכול לכתוב לאובייקט ברמת שלמות גבוהה משלו."
        elif r < 0.75: # Unix Perms
            perms = [755, 644, 700, 777, 400]
            p = random.choice(perms)
            q_text = f"נתון קובץ עם הרשאות {p}. האם משתמש שאינו הבעלים ואינו בקבוצה יכול לקרוא אותו?"
            ans = "כן" if (p % 10) >= 4 else "לא"
            opts = ["כן", "לא", "רק אם ה-Sticky Bit דלוק", "רק ב-Windows"]
            topic = "הרשאות Unix"
            exp = "הספרה האחרונה מייצגת את Others. ערך של 4 ומעלה כולל הרשאת קריאה."
        else: # Crypto/General
            crypto_q = [
                ("איזה אלגוריתם הוא הצפנה סימטרית?", "AES", ["RSA", "SHA-256", "Diffie-Hellman"]),
                ("מה היתרון של Salt?", "הגנה מפני Rainbow Tables", ["הצפנה מהירה יותר", "מניעת SQL Injection", "חתימה דיגיטלית"]),
                ("מהו SUID?", "הרצת קובץ בהרשאות הבעלים", ["מחיקת קבצים של אחרים", "הצפנת הדיסק", "ניהול משימות"]),
                ("מהו ASLR?", "הגרלת כתובות בזיכרון", ["מניעת גלישת חוצץ", "חתימת קוד", "סינון חומת אש"])
            ]
            q_data = random.choice(crypto_q)
            q_text = q_data[0]
            ans = q_data[1]
            opts = [ans] + q_data[2]
            topic = "אבטחה כללית"
            exp = "זהו מושג ליבה באבטחת מערכות תוכנה."

        random.shuffle(opts)
        questions.append({
            "id": i + 1,
            "topic": topic,
            "question": q_text,
            "options": opts,
            "answer": ans,
            "explanation": exp
        })
    return questions

def generate_concepts(count):
    concepts = []
    pool = [
        ("ASLR", "מנגנון המגריל את כתובות הזיכרון של התוכנית כדי למנוע ניצול פגיעויות זיכרון."),
        ("DEP", "מנגנון המסמן אזורי זיכרון כלא-ניתנים-להרצה (NX) כדי למנוע הרצת קוד זדוני מה-Stack."),
        ("SUID", "ביט הרשאה המאפשר הרצת קובץ עם הרשאות הבעלים שלו."),
        ("Salt", "מחרוזת אקראית המתווספת לסיסמה לפני ה-Hashing כדי למנוע התקפות Rainbow Tables."),
        ("RSA", "אלגוריתם הצפנה אסימטרי המבוסס על הקושי בפירוק מספרים גדולים לגורמים ראשוניים."),
        ("Perfect Forward Secrecy", "תכונה המבטיחה שפריצה למפתח הפרטי הקבוע לא תחשוף מפתחות הצפנה של שיחות עבר."),
        ("Man-in-the-Middle", "התקפה שבה התוקף מצותת או משנה את התקשורת בין שני צדדים בלי שהם ידעו.")
    ]
    
    for i in range(count):
        item = random.choice(pool)
        is_tf = random.random() > 0.5
        concepts.append({
            "type": "נכון / לא נכון" if is_tf else "הגדר מושג",
            "q": item[0] if not is_tf else f"האם {item[0]} משמש ל-{item[1][:30]}...",
            "a": item[1]
        })
    return concepts

if __name__ == "__main__":
    mcqs = generate_mcqs(2000)
    with open("questions.json", "w", encoding="utf-8") as f:
        json.dump(mcqs, f, ensure_ascii=False, indent=2)
    
    concepts = generate_concepts(1000)
    with open("concepts.json", "w", encoding="utf-8") as f:
        json.dump(concepts, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {len(mcqs)} MCQs and {len(concepts)} Concepts.")
