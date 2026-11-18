import re

RULES = [
    ("Asks for a fee or deposit",
     r"(registration|processing|training|application|admin|medical|visa|interview)\s+fee|pay\s+(a\s+|an\s+)?(fee|deposit)|send\s+(money|ksh|kes)|refundable deposit", 30),
    ("Asks for sensitive details (ID, bank, PIN, password)",
     r"(id|passport)\s+(copy|number|photo)|bank\s+(details|account)|\bpin\b|password|m-?pesa\s+(pin|code)", 25),
    ("Contact only via WhatsApp/Telegram",
     r"(whatsapp|telegram)\s+(only|us|on|number)|contact.{0,20}(whatsapp|telegram)", 15),
    ("Free email address used as employer contact",
     r"[\w.+-]+@(gmail|yahoo|hotmail|outlook)\.com", 15),
    ("Guaranteed job or no interview",
     r"guaranteed\s+(job|employment|placement)|no\s+interview|no\s+experience\s+(needed|required)|hired\s+immediately", 15),
    ("Unrealistic pay claims",
     r"earn\s+(up\s+to\s+)?(ksh|kes|\$)?\s?[\d,]{4,}\s*(per|a|/)\s*(day|week)|quick\s+money|easy\s+money", 15),
    ("Overseas recruitment pressure",
     r"(dubai|qatar|saudi|kuwait|oman)\b.{0,60}(agent|agency|visa|ticket)", 15),
    ("Urgency or pressure language",
     r"urgent(ly)?|limited\s+(slots|spaces|vacancies)|apply\s+now|today\s+only|act\s+fast", 10),
]


def screen_advert(text):
    indicators, score = [], 0
    for label, pattern, weight in RULES:
        if re.search(pattern, text, re.IGNORECASE):
            indicators.append(label)
            score += weight
    score = min(score, 100)
    level = "High" if score >= 60 else "Medium" if score >= 30 else "Low"
    return {"score": score, "level": level, "indicators": indicators}