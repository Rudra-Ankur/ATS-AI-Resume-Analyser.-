"""Explainable, rule-based ATS scoring. Every point is traceable to a rule."""
import re

ACTION_VERBS = {"built", "developed", "designed", "implemented", "created", "led", "optimized",
                "improved", "reduced", "increased", "automated", "deployed", "analyzed",
                "engineered", "integrated", "managed", "launched", "architected", "trained"}
WEAK_PHRASES = ["responsible for", "worked on", "helped with", "involved in", "duties included"]
METRIC = re.compile(r"\d+\s?(%|x|k|\+)|\$\s?\d|\b\d{2,}\b")


def _bullets(text: str) -> list[str]:
    out = []
    for l in text.splitlines():
        l = l.strip()
        if len(l) > 25:
            out.append(re.sub(r"^[\u2022\-*\u25cf\u25aa]\s*", "", l))
    return out


def ats_score(text: str, sections: dict, contact: dict, skills: list[str]) -> dict:
    breakdown, tips = {}, []

    # Contact info (15)
    pts = 5 * bool(contact["email"]) + 5 * bool(contact["phone"]) + 5 * bool(contact["linkedin"] or contact["github"])
    breakdown["Contact info"] = (pts, 15)
    if not contact["email"]: tips.append("Add a professional email address.")
    if not contact["phone"]: tips.append("Add a phone number.")
    if not (contact["linkedin"] or contact["github"]): tips.append("Add your LinkedIn and/or GitHub link.")

    # Sections (25)
    core = ["education", "skills", "experience", "projects"]
    present = [s for s in core if s in sections and sections[s]]
    breakdown["Core sections"] = (round(25 * len(present) / len(core)), 25)
    for s in core:
        if s not in present:
            tips.append(f"Add a clear '{s.title()}' section heading.")

    # Skills (20)
    breakdown["Skills coverage"] = (min(20, len(skills) * 2), 20)
    if len(skills) < 10: tips.append("List more relevant technical skills (aim for 10+).")

    # Bullets: metrics + action verbs + weak phrases
    body = "\n".join(sections.get(k, "") for k in ("experience", "projects")) or text
    bullets = _bullets(body)
    n = max(len(bullets), 1)
    with_metric = sum(bool(METRIC.search(b)) for b in bullets)
    with_verb = sum(b.split()[0].lower().rstrip(",") in ACTION_VERBS for b in bullets if b.split())
    weak = [b for b in bullets if any(w in b.lower() for w in WEAK_PHRASES)]

    breakdown["Quantified achievements"] = (round(20 * min(1, with_metric / (0.5 * n))), 20)
    breakdown["Action verbs"] = (round(10 * min(1, with_verb / (0.6 * n))), 10)
    if with_metric < 0.3 * n:
        tips.append(f"Only {with_metric}/{len(bullets)} bullets contain numbers. Add metrics (%, users, time saved).")
    if with_verb < 0.5 * n:
        tips.append("Start more bullets with strong action verbs (Built, Optimized, Reduced...).")
    for b in weak[:3]:
        tips.append(f"Replace weak phrasing: \"{b[:70]}...\"")
    long_b = [b for b in bullets if len(b.split()) > 35]
    if long_b: tips.append(f"{len(long_b)} bullet(s) exceed 35 words. Keep bullets to 1-2 lines.")

    # Length (10)
    words = len(text.split())
    ok = 250 <= words <= 900
    breakdown["Length"] = (10 if ok else 5, 10)
    if words < 250: tips.append("Resume looks too short. Add detail on projects and experience.")
    if words > 900: tips.append("Resume is long. Aim for one page for fresher/early-career roles.")

    total = sum(p for p, _ in breakdown.values())
    return {"score": total, "breakdown": breakdown, "suggestions": tips}
