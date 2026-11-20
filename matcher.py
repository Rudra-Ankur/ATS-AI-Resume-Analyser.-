"""Resume <-> job description matching: TF-IDF cosine + skill overlap."""
from .skills import extract_skills


def match_job(resume_text: str, jd_text: str) -> dict:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    m = vec.fit_transform([resume_text, jd_text])
    cosine = float(cosine_similarity(m[0], m[1])[0][0])

    r_sk, j_sk = set(extract_skills(resume_text)), set(extract_skills(jd_text))
    matched = sorted(r_sk & j_sk)
    missing = sorted(j_sk - r_sk)
    coverage = len(matched) / len(j_sk) if j_sk else cosine

    score = round(100 * (0.6 * coverage + 0.4 * min(1, cosine * 2)), 1)
    return {"match_score": score, "cosine": round(cosine, 3),
            "matched_skills": matched, "missing_skills": missing}
