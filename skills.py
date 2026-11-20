"""Skill taxonomy and extraction. BPO is the primary domain, tech is secondary."""
import re

SKILLS = {
    # ---------- BPO / customer support (primary) ----------
    "bpo": ["customer service", "customer support", "voice process", "non-voice process",
            "chat support", "email support", "inbound", "outbound", "telecalling", "call center",
            "call handling", "technical support", "back office", "data entry", "typing speed",
            "complaint resolution", "escalation handling", "upselling", "cross-selling",
            "lead generation", "collections", "billing", "kyc", "order processing",
            "first call resolution", "customer retention", "customer satisfaction"],
    "bpo_metrics": ["csat", "nps", "aht", "sla", "kpi", "fcr", "quality score", "adherence",
                    "call quality", "target achievement"],
    "bpo_tools": ["crm", "zendesk", "freshdesk", "salesforce", "ticketing", "avaya", "five9",
                  "genesys", "servicenow", "ms office", "ms excel", "ms word", "email etiquette"],
    "soft_skill": ["communication skills", "english", "hindi", "active listening", "problem solving",
                   "time management", "rotational shifts", "team handling", "empathy",
                   "adaptability", "negotiation", "multitasking", "conflict resolution"],
    # ---------- Tech (secondary) ----------
    "language": ["python", "java", "c", "c++", "c#", "javascript", "typescript", "sql", "go",
                 "rust", "kotlin", "php", "r", "bash", "html", "css"],
    "framework": ["flask", "django", "fastapi", "spring boot", "spring", "react", "angular",
                  "node.js", "express", "streamlit", "pandas", "numpy", "scikit-learn",
                  "tensorflow", "pytorch", "spacy", "hibernate", "bootstrap", "tailwind"],
    "database": ["mysql", "postgresql", "mongodb", "sqlite", "oracle", "redis", "firebase"],
    "tool": ["git", "github", "docker", "kubernetes", "aws", "azure", "gcp", "linux", "jenkins",
             "postman", "jira", "ci/cd", "rest api", "tableau", "power bi", "excel"],
    "concept": ["machine learning", "deep learning", "nlp", "data structures", "algorithms",
                "oop", "dbms", "operating systems", "computer networks", "microservices",
                "data analysis", "agile"],
}
BPO_CATEGORIES = {"bpo", "bpo_metrics", "bpo_tools", "soft_skill"}

ALIASES = {"js": "javascript", "postgres": "postgresql", "node": "node.js", "ml": "machine learning",
           "k8s": "kubernetes", "restful": "rest api", "data structure": "data structures",
           "customer care": "customer service", "non voice": "non-voice process",
           "telecaller": "telecalling", "tele calling": "telecalling", "call centre": "call center",
           "first contact resolution": "first call resolution", "average handling time": "aht",
           "customer satisfaction score": "csat", "excel": "ms excel", "microsoft office": "ms office",
           "communication": "communication skills", "typing": "typing speed"}

# Short words that are also common English: match only in this exact capitalisation.
CASE_SENSITIVE = {"go": "Go", "r": "R", "c": "C", "express": "Express"}

ALL_SKILLS = {s: cat for cat, lst in SKILLS.items() for s in lst}


def _pattern(skill: str) -> re.Pattern:
    # lookarounds instead of \b so "c++", "c#", "node.js" match correctly
    if skill in CASE_SENSITIVE:
        return re.compile(r"(?<![\w+#])" + re.escape(CASE_SENSITIVE[skill]) + r"(?![\w+#])")
    return re.compile(r"(?<![\w+#])" + re.escape(skill) + r"(?![\w+#])", re.I)


_PATTERNS = {s: _pattern(s) for s in ALL_SKILLS}
_ALIAS_PATTERNS = {a: (_pattern(a), t) for a, t in ALIASES.items()}


def extract_skills(text: str) -> list[str]:
    found = {s for s, p in _PATTERNS.items() if p.search(text)}
    found |= {t for _, (p, t) in _ALIAS_PATTERNS.items() if p.search(text)}
    return sorted(found)


def detect_profile(skills: list[str]) -> str:
    """Guess 'bpo' or 'tech' from detected skills. Ties and empty -> bpo (primary)."""
    bpo = sum(ALL_SKILLS.get(s) in BPO_CATEGORIES for s in skills)
    tech = len(skills) - bpo
    return "tech" if tech > bpo else "bpo"


def categorize(skills: list[str]) -> dict:
    out = {}
    for s in skills:
        out.setdefault(ALL_SKILLS.get(s, "other"), []).append(s)
    return out