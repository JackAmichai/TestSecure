/**
 * TestSecure AI Chatbot
 * Trained on 300 questions + 88 concepts + past exam materials
 * Can ask questions and evaluate user answers
 */

class TestSecureChatbot {
    constructor() {
        this.questions = [];
        this.concepts = [];
        this.currentQuestion = null;
        this.score = 0;
        this.totalAnswered = 0;
        this.studyMode = 'random'; // 'random', 'topic', 'exam'
        this.currentTopic = null;
        this.examQuestions = [];
        this.examIndex = 0;
    }

    async init() {
        try {
            const [qRes, cRes] = await Promise.all([
                fetch('questions.json'),
                fetch('concepts.json')
            ]);
            this.questions = await qRes.json();
            this.concepts = await cRes.json();
            console.log(`Chatbot initialized with ${this.questions.length} questions and ${this.concepts.length} concepts`);
            return true;
        } catch (e) {
            console.error('Error loading chatbot data:', e);
            return false;
        }
    }

    // Get random question
    getRandomQuestion(topic = null) {
        let filtered = this.questions;
        if (topic) {
            filtered = this.questions.filter(q => q.topic === topic);
        }
        if (filtered.length === 0) return null;
        this.currentQuestion = filtered[Math.floor(Math.random() * filtered.length)];
        return this.currentQuestion;
    }

    // Get question by topic
    getTopics() {
        return [...new Set(this.questions.map(q => q.topic))];
    }

    // Start exam mode (5 random questions)
    startExam() {
        this.examQuestions = [];
        this.examIndex = 0;
        const topics = this.getTopics();
        
        // Pick 5 random questions from different topics if possible
        for (let i = 0; i < 5; i++) {
            const q = this.getRandomQuestion();
            if (q) this.examQuestions.push(q);
        }
        
        return this.examQuestions;
    }

    // Get current exam question
    getExamQuestion() {
        if (this.examIndex >= this.examQuestions.length) return null;
        return this.examQuestions[this.examIndex];
    }

    // Move to next exam question
    nextExamQuestion() {
        this.examIndex++;
        return this.getExamQuestion();
    }

    // Evaluate user's answer
    evaluateAnswer(userAnswer) {
        if (!this.currentQuestion && this.examQuestions.length === 0) {
            return { correct: false, message: 'אין שאלה פעילה', explanation: '' };
        }

        const q = this.currentQuestion || this.examQuestions[this.examIndex - 1];
        if (!q) {
            return { correct: false, message: 'שגיאה בשאלה', explanation: '' };
        }

        const isCorrect = userAnswer.trim() === q.answer.trim();
        this.totalAnswered++;
        
        if (isCorrect) {
            this.score++;
        }

        return {
            correct: isCorrect,
            message: isCorrect ? '✅ תשובה נכונה!' : `❌ תשובה לא נכונה. התשובה הנכונה היא: ${q.answer}`,
            explanation: q.explanation,
            correctAnswer: q.answer,
            score: `${this.score}/${this.totalAnswered}`,
            percentage: Math.round((this.score / this.totalAnswered) * 100)
        };
    }

    // Get a concept flashcard
    getRandomConcept() {
        if (this.concepts.length === 0) return null;
        return this.concepts[Math.floor(Math.random() * this.concepts.length)];
    }

    // Ask True/False question
    askTrueFalse() {
        const concept = this.getRandomConcept();
        if (!concept) return null;
        
        return {
            question: concept.q,
            type: concept.type,
            answer: concept.a,
            explanation: concept.explanation || ''
        };
    }

    // Get study tip based on topic
    getStudyTip(topic = null) {
        const tips = {
            'מודל Bell-LaPadula': 'זכור: BLP = סודיות. Simple Security = No Read Up (index נמוך יותר = סיווג גבוהה יותר). *-Property = No Write Down.',
            'מודל Biba': 'זכור: Biba = שלמות. Simple Integrity = No Read Down (index גבוהה יותר = שלמות גבוהה יותר). *-Integrity = No Write Up.',
            'הרשאות Unix': 'זכור: ספרה ראשונה=בעלים, שנייה=קבוצה, שלישית=אחרים. 4=Read, 2=Write, 1=eXecute. SUID=4xxx, SGID=2xxx, Sticky=1xxx.',
            'בקרת גישה': 'DAC=בעלים קובע, MAC=מערכת קובעת, RBAC=לפי תפקיד. ACL=רשימת הרשאות, C-List=רשימת יכולת.',
            'הצפנה סימטרית': 'AES=סטנדרט (128/256 ביט), DES=ישן (56 ביט). ECB=חושף דפוסים! CBC=מונע דפוסים עם IV.',
            'הצפנה אסימטרית': 'RSA=מבוסס על פירוק ראשוניים (איטי). Diffie-Hellman=החלפת מפתחות. חתימה=פרטי לחתימה, ציבורי לאימות.',
            'Hash ו-MAC': 'Hash=חד-כיווני (SHA-256). HMAC=Hash+מפתח סודי (מאמת מקור). Salt=מונע Rainbow Tables.',
            'Kerberos': 'AS=אימות ו-TGT, TGS=מעניק כרטיסי שירות. הצפנה סימטרית. אין העברת סיסמאות ברשת.',
            'SSL/TLS': 'Handshake=הסכמה על פרוטוקול ומפתחות. Perfect Forward Secrecy=מפתחות זמניים (DHE/ECDHE).',
            'חומות אש (Firewalls)': 'Stateless=בודק חבילות בנפרד. Stateful=זוכר חיבורים. Proxy=בודק תוכן יישום.',
            'Buffer Overflow': 'Stack=גלישת מחסנית. DEP=NX bit. ASLR=רנדומליזציה. Canary=ערך אקראי לפני Return Address.',
            'פגיעויות ווב': 'SQL Injection=הזרקת שאילתות SQL. XSS=הזרקת JavaScript. CSRF=גרימת פעולה לא רצויה.',
            'תוכנות זדוניות': 'Virus=משתכפל בתוכניות. Worm=משתכפל ברשת. Trojan=נראה חוקי. Ransomware=מצפין ודורש כופר.',
            'IDS/IPS': 'IDS=מתריע. IPS=מונע. Signature=לפי חתימה ידועה. Anomaly=לפי סטייה מהרגיל.',
            'אנטרופיה וזרימת מידע': 'H=log₂(אפשרויות לפני/אחרי). Covert Channel=תקשורת סמויה. Zero-day=פגיעות לא ידועה.',
            'אימות (Authentication)': 'MFA=שני גורמים. 2FA=דו-שלבי. Biometrics=תכונות פיזיות. Brute Force=ניסיון סיסמאות רבים.'
        };

        if (topic && tips[topic]) {
            return tips[topic];
        }
        
        // Return random tip
        const allTips = Object.values(tips);
        return allTips[Math.floor(Math.random() * allTips.length)];
    }

    // Get statistics
    getStats() {
        const topics = this.getTopics();
        const topicCounts = {};
        topics.forEach(t => {
            topicCounts[t] = this.questions.filter(q => q.topic === t).length;
        });
        
        return {
            totalQuestions: this.questions.length,
            totalConcepts: this.concepts.length,
            totalTopics: topics.length,
            topicCounts: topicCounts,
            score: `${this.score}/${this.totalAnswered}`,
            percentage: this.totalAnswered > 0 ? Math.round((this.score / this.totalAnswered) * 100) : 0
        };
    }
}

// Export for use in HTML
window.TestSecureChatbot = TestSecureChatbot;
