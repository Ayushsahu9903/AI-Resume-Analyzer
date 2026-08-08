from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
import pandas as pd
import json
from services.JobInfoExtraction import JobInfoExtraction
from services.Rules import Rules
from source.db_helpers.db_connection import database
from source.schemas.matched_resume import ResumeMatchedModel
from source.schemas.jobextracted import JobExtractedModel
import ast


def transform_dataframe_to_json(dataframe):
    """Transforms a dataframe into a JSON string."""
    result = dataframe.to_json(orient="records")
    parsed = json.loads(result)
    json_data = json.dumps(parsed, indent=4)
    return json_data


app = FastAPI(
    title="AI Resume Analyzer",
    description="An AI-powered API to extract job info and match resumes using NLP.",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "message": "✅ AI Resume Analyzer API is running.",
        "docs": "/docs",
        "endpoints": ["/extraction", "/matching", "/top_resumes"]
    }


@app.get("/extraction")
async def extraction():
    degrees_patterns_path = 'Resources/data/degrees.jsonl'
    majors_patterns_path = 'Resources/data/majors.jsonl'
    skills_patterns_path = 'Resources/data/skills.jsonl'
    jobs = pd.read_csv('Resources/data/job descriptions.csv', index_col=0)
    jobs = jobs[['Job description']]
    job_extraction = JobInfoExtraction(
        skills_patterns_path, majors_patterns_path, degrees_patterns_path, jobs
    )
    jobs = job_extraction.extract_entities(jobs)

    for i, row in jobs.iterrows():
        minimum_degree_level = jobs['Minimum degree level'][i]
        acceptable_majors = jobs['Acceptable majors'][i]
        skills = jobs['Skills'][i]

        job_extracted = JobExtractedModel(
            minimum_degree_level=minimum_degree_level if minimum_degree_level else '',
            acceptable_majors=acceptable_majors if acceptable_majors else [],
            skills=skills if skills else []
        )
        job_extracted = jsonable_encoder(job_extracted)
        database.get_collection("jobsextracted").insert_one(job_extracted)

    jobs_json = transform_dataframe_to_json(jobs)
    return json.loads(jobs_json)


def modifying_type_resume(resumes):
    for i in range(len(resumes["degrees"])):
        resumes["degrees"][i] = ast.literal_eval(resumes["degrees"][i])
    for i in range(len(resumes["skills"])):
        resumes["skills"][i] = ast.literal_eval(resumes["skills"][i])
    return resumes


def modifying_type_job(jobs):
    for i in range(len(jobs["Skills"])):
        jobs["Skills"][i] = ast.literal_eval(jobs["Skills"][i])
    return jobs


@app.get("/matching")
async def matching():
    with open('Resources/data/labels.json') as fp:
        labels = json.load(fp)
    jobs = pd.read_csv('Resources/data/job_description_by_spacy.csv', index_col=0)
    resumes = pd.read_csv('Resources/data/resumes_by_spacy.csv', index_col=0)
    resumes = modifying_type_resume(resumes)
    jobs = modifying_type_job(jobs)
    rules = Rules(labels, resumes, jobs)
    job_indexes = [0, 1, 2, 3, 4]

    # FIX: pd.DataFrame.append() removed in pandas 2.x — use pd.concat() instead
    all_matched = []
    for job_index in job_indexes:
        resumes_matched = rules.matching_score(resumes, jobs, job_index)
        all_matched.append(resumes_matched)

        for i, row in resumes_matched.iterrows():
            id_resume = resumes_matched['_id'][i]
            degree_matching = float(resumes_matched['Degree job ' + str(job_index) + ' matching'][i])
            major_matching = float(resumes_matched['Major job ' + str(job_index) + ' matching'][i])
            skills_semantic_matching = float(
                resumes_matched['Skills job ' + str(job_index) + ' semantic matching'][i]
            )
            matching_score = float(resumes_matched['matching score job ' + str(job_index)][i])

            matched_resume = ResumeMatchedModel(
                id_resume=id_resume if id_resume else '',
                job_index=job_index if job_index else 0,
                degree_matching=degree_matching if degree_matching else 0,
                major_matching=major_matching if major_matching else 0,
                skills_semantic_matching=skills_semantic_matching if skills_semantic_matching else 0,
                matching_score=matching_score if matching_score else 0
            )
            matched_resume = jsonable_encoder(matched_resume)
            # FIX: motor async insert — use await properly
            await database.get_collection("matches").insert_one(matched_resume)

    # FIX: use pd.concat instead of deprecated .append()
    resumes_matched_jobs = pd.concat(all_matched, ignore_index=True)
    resumes_matched_json = transform_dataframe_to_json(resumes_matched_jobs)
    return json.loads(resumes_matched_json)


@app.get("/top_resumes")
async def top_resumes():
    # FIX: renamed function (was duplicate name 'extraction') — now 'top_resumes'
    top = database.matches.find().sort("matching_score", -1).limit(5)
    result = []
    top = await top.to_list(None)
    for x in top:
        result.append(x)
    return jsonable_encoder(result)
