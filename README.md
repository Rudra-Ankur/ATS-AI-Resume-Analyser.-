# AI Resume Analyser

Parses PDF/DOCX resumes, scores ATS-readiness with an explainable rubric, matches against a job
description (TF-IDF cosine + skill overlap), and stores history in MySQL. Built with Python, Streamlit, MySQL.

## Setup
```bash
python -m venv venv && source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
mysql -u root -p < schema.sql
cp .env.example .env                                # then edit DB_PASSWORD
streamlit run app.py
pytest
```
The app runs without MySQL too (history is just disabled).

## Scoring rubric (100)
Contact 15 | Core sections 25 | Skills 20 | Quantified achievements 20 | Action verbs 10 | Length 10

## Structure
```
app.py              Streamlit UI
analyzer/parser.py  text extraction, contact, sections
analyzer/skills.py  skill taxonomy + extraction
analyzer/scoring.py ATS scoring + suggestions
analyzer/matcher.py JD matching
analyzer/db.py      MySQL layer
schema.sql          tables
tests/              pytest
```

## Ideas to extend
Sentence-transformer embeddings, spaCy NER, LLM-written feedback, evaluate skill extraction on 30 labeled resumes,
Docker, deploy to Render.
