# AI Resume Analyzer

An AI-powered Resume Analyzer built using FastAPI, NLP, and Machine Learning to match resumes with job descriptions and calculate similarity scores.

---

# Features

- Resume and Job Description Matching
- Skill Extraction using NLP
- Resume Ranking System
- Semantic Similarity Matching
- Education & Major Matching
- AI-based Candidate Screening
- FastAPI Backend
- Docker Support

---

# Tech Stack

## Backend
- FastAPI
- Python

## AI / NLP
- SpaCy
- Sentence Transformers
- BERT
- Cosine Similarity

## Tools
- Docker
- Pandas
- NumPy
- Scikit-learn

---

# Project Workflow

1. Extract information from job descriptions
2. Extract resume skills and qualifications
3. Compare resumes with job descriptions
4. Calculate similarity score
5. Rank resumes based on matching score

---

# AI Models Used

The project uses NLP embedding models such as:

- bert-base-nli-mean-tokens
- all-mpnet-base-v2
- MiniLM models

These models generate semantic embeddings for resume-job matching.

---

# Similarity Calculation

The system uses Cosine Similarity to compare resume embeddings with job description embeddings.

---

# Project Structure

```bash
Resources/
services/
source/

main.py
Dockerfile
docker-compose.yml
requirements.txt
README.md