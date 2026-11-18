import re

KNOWN_SKILLS = [
    "python", "django", "flask", "java", "javascript", "typescript", "react",
    "node.js", "php", "laravel", "c++", "c#", "sql", "postgresql", "mysql",
    "mongodb", "html", "css", "git", "docker", "linux", "aws", "azure",
    "machine learning", "networking", "cybersecurity", "excel", "communication",
    "teamwork", "problem solving", "rest api", "tailwind", "htmx",
]


def _found(skill, text):
    return re.search(r"(?<![\w+#])" + re.escape(skill) + r"(?![\w+#])", text, re.IGNORECASE)


def match_skills(text, confirmed_names):
    confirmed = {n.strip().lower() for n in confirmed_names}
    required = {s for s in KNOWN_SKILLS if _found(s, text)}
    required |= {c for c in confirmed if _found(c, text)}
    matched = sorted(required & confirmed)
    missing = sorted(required - confirmed)
    score = round(100 * len(matched) / len(required)) if required else 0
    return {"matched": matched, "missing": missing, "score": score}