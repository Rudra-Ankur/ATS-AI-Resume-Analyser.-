import streamlit as st
from analyzer import parser, skills as sk, scoring, matcher, db

st.set_page_config(page_title="AI Resume Analyser", page_icon="📄", layout="wide")
st.title("📄 AI Resume Analyser")
st.caption("Upload a resume, optionally paste a job description, and get an explainable ATS score.")

db_ok = db.available()
if not db_ok:
    st.sidebar.warning("MySQL not connected. Analysis works, but history is not saved.")

tab_analyse, tab_history = st.tabs(["Analyse", "History"])

with tab_analyse:
    left, right = st.columns(2)
    file = left.file_uploader("Resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    jd_title = right.text_input("Job title (optional)")
    jd = right.text_area("Job description (optional)", height=160)

    if file and st.button("Analyse", type="primary"):
        try:
            text = parser.extract_text(file.getvalue(), file.name)
        except Exception as e:
            st.error(f"Could not read file: {e}"); st.stop()
        if len(text) < 50:
            st.error("Little or no text found. If this is a scanned PDF, it needs OCR."); st.stop()

        contact = parser.extract_contact(text)
        sections = parser.detect_sections(text)
        found = sk.extract_skills(text)
        ats = scoring.ats_score(text, sections, contact, found)
        match = matcher.match_job(text, jd) if jd.strip() else None

        c1, c2 = st.columns(2)
        c1.metric("ATS score", f"{ats['score']}/100")
        if match: c2.metric("Job match", f"{match['match_score']}%")

        st.subheader("Score breakdown")
        for name, (got, out_of) in ats["breakdown"].items():
            st.write(f"**{name}**: {got}/{out_of}")
            st.progress(got / out_of)

        st.subheader("Suggestions")
        for t in ats["suggestions"] or ["Looks solid. Nothing major to fix."]:
            st.write("• " + t)

        st.subheader("Detected skills")
        for cat, lst in sk.categorize(found).items():
            st.write(f"**{cat.title()}:** " + ", ".join(lst))

        if match:
            st.subheader("Job match details")
            st.success("Matched: " + (", ".join(match["matched_skills"]) or "none"))
            st.error("Missing: " + (", ".join(match["missing_skills"]) or "none"))

        with st.expander("Parsed profile"):
            st.json({"contact": contact, "sections_found": list(sections)})

        if db_ok:
            try:
                db.save_analysis(file.name, text, found, ats["score"], jd_title, jd or None,
                                 match["match_score"] if match else None)
                st.toast("Saved to MySQL")
            except Exception as e:
                st.warning(f"Could not save: {e}")

with tab_history:
    if not db_ok:
        st.info("Connect MySQL to see history.")
    else:
        st.dataframe(db.history(), use_container_width=True)
        st.subheader("Most common skills across uploads")
        rows = db.top_skills()
        if rows:
            st.bar_chart({r["name"]: r["n"] for r in rows})
