# דוח מחקר - ניתוח השוואתי של מנגנוני אימות מבוססי סיסמאות
## Research Report - Comparative Analysis of Password-Based Authentication Mechanisms

**Course:** 20940 - Introduction to Cybersecurity  
**Assignment:** Programming Assignment #16  
**Date:** [Insert Date]  
**Group Members:**
- Student 1: [Name] (ID: [ID])
- Student 2: [Name] (ID: [ID])  
**GROUP_SEED:** [Calculated XOR value]

---

## תקציר / Abstract

[150-200 words]
Brief summary of the research objectives, methodology, key findings, and conclusions. Mention the hashing algorithms tested (SHA-256, bcrypt, Argon2id), protection mechanisms (rate limiting, lockout, CAPTCHA, TOTP, Pepper), and attack methods (brute-force, password spraying).

**Key findings:**
- [Finding 1]
- [Finding 2]
- [Finding 3]

---

## 1. מבוא / Introduction

### 1.1 רקע ומוטיבציה / Background and Motivation

Password-based authentication remains the primary method for user verification across digital systems. However, the security of these systems depends heavily on:
- The strength of the hashing algorithms used
- The implementation of secondary protection mechanisms
- User password selection habits

This research investigates how different combinations of these factors affect resilience against common attack methods.

### 1.2 מטרות המחקר / Research Objectives

**Primary Objective:**
To perform a reproducible experiment comparing password hashing and authentication mechanisms, examining the effectiveness of various protection mechanisms, and conducting statistical analysis of the results.

**Secondary Objectives:**
1. Measure time-to-breach and success rates under various protection mechanisms
2. Quantify the impact of each protection mechanism individually and in combination
3. Evaluate the usability-security trade-off in each approach
4. Produce a concise research report summarizing experimental findings

### 1.3 היקף המחקר / Research Scope

- **Attack Surface:** Online attacks only (REST API)
- **Hashing Algorithms:** SHA-256+salt, bcrypt (cost=12), Argon2id (default params)
- **Protection Mechanisms:** Rate limiting, account lockout, CAPTCHA simulation, TOTP, Pepper
- **Attack Methods:** Brute-force, password spraying
- **Dataset:** 30 synthetic users (10 weak, 10 medium, 10 strong passwords)

---

## 2. רקע תיאורטי / Theoretical Background

### 2.1 אלגוריתמי גיבוב / Hashing Algorithms

#### SHA-256
- Fast cryptographic hash function
- Requires additional measures (salt, pepper, key stretching)
- Vulnerable to GPU-accelerated attacks without proper hardening

#### bcrypt
- Designed specifically for password hashing
- Built-in salt generation
- Adjustable cost factor (work factor)
- Memory-hard to resist ASIC attacks

#### Argon2id
- Winner of Password Hashing Competition (2015)
- Hybrid mode (Argon2i + Argon2d)
- Configurable memory, time, and parallelism parameters
- Resistant to side-channel and GPU attacks

### 2.2 מנגנוני הגנה / Protection Mechanisms

#### Salt
- Unique random value per user
- Prevents rainbow table attacks
- Stored alongside password hash

#### Pepper
- Global secret value
- Stored separately from database
- Adds additional layer if database is compromised

#### Rate Limiting
- Limits number of requests per time window
- Slows down automated attacks
- Can affect legitimate users during high traffic

#### Account Lockout
- Temporarily disables account after N failed attempts
- Effective against brute-force attacks
- Risk of denial-of-service if abused

#### CAPTCHA
- Distinguishes humans from bots
- Adds friction to user experience
- Can be bypassed by sophisticated attackers

#### TOTP (Time-based One-Time Password)
- Second factor authentication
- 30-second validity window
- Requires additional device/app
- Highly effective against credential theft

### 2.3 שיטות תקיפה / Attack Methods

#### Brute-Force
- Systematic enumeration of all possible passwords
- Targets single account
- Effectiveness depends on:
  - Password strength
  - Hashing algorithm computational cost
  - Protection mechanisms in place

#### Password Spraying
- Tests common passwords across many accounts
- Evades per-user rate limiting
- Exploits weak password selection
- Requires global rate limiting to mitigate

---

## 3. מתודולוגיה / Methodology

### 3.1 תצורה ניסויית / Experimental Setup

#### Hardware & Software
- **Server:** [Describe your system specs]
- **OS:** [Operating System]
- **Python Version:** [Version]
- **Libraries:** Flask, bcrypt, argon2-cffi, pyotp

#### Network Configuration
- Local server (127.0.0.1:5000)
- REST API endpoints: /register, /login, /login_totp
- No external network access

### 3.2 יצירת נתוני בדיקה / Test Data Generation

**User Dataset:**
- 30 synthetic users
- 3 categories (10 users each):
  - **Weak:** 7-8 digit numbers, simple lowercase strings
  - **Medium:** 8-10 character alphanumeric mixed case
  - **Strong:** 12-14 characters with symbols, mixed case

**Password Examples:**
- Weak: `42400147`, `70336321`, `8325861`
- Medium: `yy93n52s`, `pf48s5ypp`, `8xz0wp27t`
- Strong: `*KjtkMh3p_VbG`, `c9u_3v#!KCyHJ!`

**Special Password:**
- One password equals GROUP_SEED for tracking purposes

### 3.3 פרוטוקול ניסוי / Experiment Protocol

1. **Baseline Testing** (No protections)
   - Run brute-force attack on weak password
   - Run password spraying across all users
   - Collect: attempts, time, success rate

2. **Single Protection Testing**
   - Test each protection mechanism individually:
     - Rate limiting only
     - Lockout only
     - CAPTCHA only
   - Compare results to baseline

3. **Combined Protection Testing**
   - Test combinations:
     - Lockout + Rate limiting
     - Lockout + Rate limiting + CAPTCHA
     - All protections + TOTP

4. **Hashing Algorithm Comparison**
   - Repeat key experiments with:
     - SHA-256
     - bcrypt
     - Argon2id
   - Measure latency and effectiveness differences

5. **Pepper Testing**
   - Run experiments with and without PEPPER
   - Compare effectiveness of database breach mitigation

### 3.4 משתנים מבוקרים / Controlled Variables

- Same GROUP_SEED throughout
- Consistent password datasets
- Fixed protection parameters (unless testing parameter variation)
- Same attack dictionaries
- Controlled environmental conditions

### 3.5 מגבלות הניסוי / Experiment Constraints

- **Maximum attempts:** 50,000 per configuration (up to 1,000,000 if needed)
- **Time limit:** 2 hours per experiment
- **Server capacity:** Single-threaded Flask development server
- **Attack rate:** Limited by network latency and protection mechanisms

---

## 4. תוצאות / Results

### 4.1 נתונים גולמיים / Raw Data

[Reference to attempts.log files, summary statistics]

**Total Experiments Conducted:** [Number]  
**Total Authentication Attempts:** [Number]  
**Total Experiment Duration:** [Hours]

### 4.2 השוואת אלגוריתמי גיבוב / Hashing Algorithm Comparison

**Table 1: Hashing Performance**

| Hash Algorithm | Avg Latency (ms) | Attempts/sec | Time to Breach (Weak) | Time to Breach (Medium) |
|----------------|------------------|--------------|----------------------|------------------------|
| SHA-256        | [Value]          | [Value]      | [Value]              | [Value]                |
| bcrypt         | [Value]          | [Value]      | [Value]              | [Value]                |
| Argon2id       | [Value]          | [Value]      | [Value]              | [Value]                |

**Key Observations:**
- [Observation 1]
- [Observation 2]
- [Observation 3]

### 4.3 השפעת מנגנוני ההגנה / Protection Mechanisms Impact

**Table 2: Success Rate by Protection Configuration**

| Configuration          | Success Rate (Weak) | Success Rate (Medium) | Success Rate (Strong) | Avg Time to Success |
|------------------------|---------------------|----------------------|-----------------------|---------------------|
| No protections         | [%]                 | [%]                  | [%]                   | [seconds]           |
| Rate Limit             | [%]                 | [%]                  | [%]                   | [seconds]           |
| Lockout                | [%]                 | [%]                  | [%]                   | [seconds]           |
| CAPTCHA                | [%]                 | [%]                  | [%]                   | [seconds]           |
| Rate Limit + Lockout   | [%]                 | [%]                  | [%]                   | [seconds]           |
| All protections        | [%]                 | [%]                  | [%]                   | [seconds]           |
| All + TOTP             | [%]                 | [%]                  | [%]                   | [seconds]           |

**Key Observations:**
- [Observation 1]
- [Observation 2]

### 4.4 סוגי התקיפה / Attack Type Comparison

**Brute-Force vs Password Spraying:**

[Compare effectiveness, detection rates, mitigation success]

**Table 3: Attack Method Comparison**

| Metric                    | Brute-Force | Password Spraying |
|---------------------------|-------------|-------------------|
| Accounts Compromised      | [Value]     | [Value]           |
| Detection Rate            | [%]         | [%]               |
| Lockout Triggers          | [Value]     | [Value]           |
| Rate Limit Triggers       | [Value]     | [Value]           |

### 4.5 חוזק סיסמה / Password Strength Analysis

**Success Rate by Password Category:**

[Graph or table showing success rates for weak/medium/strong passwords under different configurations]

---

## 5. ניתוח ודיון / Analysis and Discussion

### 5.1 ניתוח סטטיסטי / Statistical Analysis

#### Latency Distribution
[Describe distribution patterns, compare median vs mean, discuss percentiles]

**P50, P90, P95, P99 latencies:**
- SHA-256: [values]
- bcrypt: [values]
- Argon2id: [values]

#### Time-to-Breach Analysis
[Discuss time required to breach accounts under different configurations]

#### Extrapolation for Incomplete Attacks
[For attacks that didn't succeed, estimate time to exhaust keyspace]

### 5.2 יעילות מנגנוני ההגנה / Protection Mechanism Effectiveness

#### Rate Limiting
**Advantages:**
- [List]

**Limitations:**
- [List]

**Optimal Configuration:**
- [Recommendations based on findings]

#### Account Lockout
[Similar analysis]

#### CAPTCHA
[Similar analysis]

#### TOTP
[Similar analysis]

#### Pepper
[Similar analysis]

### 5.3 פשרות בין שימושיות לאבטחה / Usability-Security Trade-offs

[Discuss how protection mechanisms affect user experience vs security gains]

**Decision Matrix:**
| Mechanism | Security Gain | Usability Impact | Implementation Cost | Recommendation |
|-----------|---------------|------------------|---------------------|----------------|
| Rate Limit| [Level]       | [Level]          | [Level]             | [Yes/No/Maybe] |
| Lockout   | [Level]       | [Level]          | [Level]             | [Yes/No/Maybe] |
| CAPTCHA   | [Level]       | [Level]          | [Level]             | [Yes/No/Maybe] |
| TOTP      | [Level]       | [Level]          | [Level]             | [Yes/No/Maybe] |
| Pepper    | [Level]       | [Level]          | [Level]             | [Yes/No/Maybe] |

### 5.4 תוקף הניסוי / Experiment Validity

#### Strengths
1. Controlled environment
2. Reproducible methodology
3. Comprehensive logging
4. Multiple configurations tested

#### Limitations
1. **Hardware:** Limited to single development machine
2. **Scale:** Small dataset (30 users)
3. **Attack Tools:** Simple custom scripts vs sophisticated tools
4. **Duration:** Time constraints limited exhaustive testing
5. **Realism:** Simplified threat model, no network variables

#### Sources of Error
1. **Time Synchronization:** TOTP timing issues
2. **Network Jitter:** Local latency variations
3. **Server Load:** Inconsistent response times under load
4. **Logging Overhead:** Impact on measured latency

#### Reproducibility
To reproduce:
1. Use provided GROUP_SEED
2. Set same environment variables (PEPPER)
3. Use same Python library versions
4. Follow documented protocol
5. Use same password datasets

---

## 6. שיקולים אתיים / Ethical Considerations

### 6.1 הצהרת ציות / Compliance Declaration

This research was conducted in full compliance with ethical guidelines:

✓ All experiments performed on local/virtual systems only  
✓ No attacks on external networks or systems  
✓ Only synthetic test data used (no real user data)  
✓ No unauthorized access attempts  
✓ Project conducted for educational purposes only  

### 6.2 שיקולי פרטיות / Privacy Considerations

- All user data is synthetic and randomly generated
- No personally identifiable information (PII) used
- Logs contain only test usernames and technical data
- No data collection from real users

### 6.3 שימוש אחראי בידע / Responsible Knowledge Use

Knowledge gained from this research should be used exclusively for:
- Improving security systems
- Educational purposes
- Defensive security measures

**Prohibited uses:**
- Unauthorized access to systems
- Malicious attacks
- Violating terms of service
- Illegal activities

---

## 7. מסקנות / Conclusions

### 7.1 ממצאים עיקריים / Key Findings

1. **Hashing Algorithms:**
   - [Key finding about relative effectiveness]
   - [Performance trade-offs]

2. **Protection Mechanisms:**
   - [Most effective combinations]
   - [Surprising results]

3. **Attack Methods:**
   - [Effectiveness comparison]
   - [Best mitigation strategies]

4. **Password Strength:**
   - [Quantified impact]
   - [Recommendations]

### 7.2 המלצות / Recommendations

**For System Administrators:**
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

**For Developers:**
1. [Recommendation 1]
2. [Recommendation 2]

**For Users:**
1. [Recommendation 1]
2. [Recommendation 2]

### 7.3 עבודה עתידית / Future Work

Potential extensions:
1. **Parameter Optimization:** Test various Argon2 parameters
2. **Distributed Attacks:** Simulate coordinated multi-source attacks
3. **Offline Attacks:** Compare online vs offline attack effectiveness
4. **Real-World Data:** Analyze breached password databases
5. **Advanced Protections:** Test behavioral analysis, ML-based detection
6. **Resource Constraints:** Performance under limited CPU/memory

---

## 8. מקורות / References

1. NIST SP 800-63B - Digital Identity Guidelines: Authentication and Lifecycle Management
2. OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/
3. RFC 6238 - TOTP: Time-Based One-Time Password Algorithm
4. Argon2: The Password Hashing Competition Winner (2015)
5. Bonneau et al., "The Science of Guessing: Analyzing an Anonymized Corpus of 70 Million Passwords"
6. Microsoft Security Blog - Password Spray Attack Detection
7. bcrypt Documentation: https://github.com/pyca/bcrypt/
8. Flask Documentation: https://flask.palletsprojects.com/

---

## נספחים / Appendices

### נספח א': קונפיגורציות מלאות / Appendix A: Full Configurations

[Include complete config_profiles.py content or key sections]

### נספח ב': דוגמאות לוגים / Appendix B: Log Samples

[Include representative log entries]

### נספח ג': קוד מקור / Appendix C: Source Code

[Reference GitHub repository]

Repository: https://github.com/JackAmichai/password-research  
Commit: [Hash]  
GROUP_SEED: [Value]

### נספח ד': תרשימים מפורטים / Appendix D: Detailed Charts

[Include visualizations: bar charts, line graphs, heatmaps showing:
- Latency distributions
- Success rates by configuration
- Time-to-breach comparisons
- Protection effectiveness]

### נספח ה': נתונים גולמיים / Appendix E: Raw Data

[Reference to attempts.log and analysis_summary.json files]

---

**Document Metadata:**
- Pages: [6-8]
- Words: [~3000-4000]
- Created: [Date]
- Last Modified: [Date]
- Version: 1.0
- GROUP_SEED: [Value]
