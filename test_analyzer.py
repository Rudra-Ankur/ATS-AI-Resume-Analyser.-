from analyzer import parser, skills, scoring

SAMPLE = """Riya Sharma
riya@example.com +91 98765 43210 github.com/riya
Education
B.Tech Computer Science, 2026
Skills
Python, Java, C, C++, MySQL, Flask, Git, Docker, REST API
Projects
- Built a Flask API serving 500+ users, reducing response time by 40%
- Developed a MySQL schema with 8 tables and indexed queries
Experience
- Responsible for testing internal tools and writing documentation
"""


def test_skill_extraction_handles_symbols():
    found = skills.extract_skills("Proficient in C++, C#, Node.js and plain C, but not Cobol")
    assert {"c++", "c#", "node.js", "c"} <= set(found)


def test_c_does_not_match_inside_words():
    assert "c" not in skills.extract_skills("Excellent communication")


def test_sections_and_contact():
    s = parser.detect_sections(SAMPLE)
    assert {"education", "skills", "projects", "experience"} <= set(s)
    c = parser.extract_contact(SAMPLE)
    assert c["email"] == "riya@example.com" and c["github"]


def test_ats_score_range_and_tips():
    s = parser.detect_sections(SAMPLE)
    r = scoring.ats_score(SAMPLE, s, parser.extract_contact(SAMPLE), skills.extract_skills(SAMPLE))
    assert 0 <= r["score"] <= 100
    assert any("weak" in t.lower() for t in r["suggestions"])
