from typing import Dict, List, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_match_score(resume: Dict, job: Dict) -> Dict:
    """Calculate match score between resume and job description."""
    # 1. Calculate skill match score
    resume_skills = set([skill.lower() for skill in resume.get("skills", [])])
    required_skills = set([skill.lower() for skill in job.get("required_skills", [])])
    preferred_skills = set([skill.lower() for skill in job.get("preferred_skills", [])])
    
    # Match skills (accounting for partial matches)
    matched_skills = []
    for job_skill in list(required_skills) + list(preferred_skills):
        for resume_skill in resume_skills:
            # Check for exact match or if job skill is contained in resume skill or vice versa
            if (job_skill == resume_skill or 
                job_skill in resume_skill or 
                resume_skill in job_skill):
                matched_skills.append(job_skill)
                break
    
    matched_skills_set = set(matched_skills)
    missing_skills = required_skills - matched_skills_set
    
    # Calculate skill score (give more weight to required skills)
    req_skill_match = len([s for s in matched_skills if s.lower() in required_skills]) / max(len(required_skills), 1)
    pref_skill_match = len([s for s in matched_skills if s.lower() in preferred_skills]) / max(len(preferred_skills), 1) if preferred_skills else 1.0
    
    # Weight: 70% required skills, 30% preferred skills
    skills_score = (req_skill_match * 0.7) + (pref_skill_match * 0.3)
    
    # 2. Calculate education match score
    resume_edu = " ".join(resume.get("education", [])).lower()
    job_edu_reqs = [req.lower() for req in job.get("education_requirements", [])]
    
    matched_education = []
    for edu_req in job_edu_reqs:
        if edu_req in resume_edu:
            matched_education.append(edu_req)
    
    education_score = len(matched_education) / max(len(job_edu_reqs), 1) if job_edu_reqs else 0.5
    
    # 3. Calculate experience match score
    resume_exp = " ".join([exp.get("description", "") for exp in resume.get("experience", [])]).lower()
    job_exp_reqs = [req.lower() for req in job.get("experience_requirements", [])]
    
    matched_exp_keywords = []
    for exp_req in job_exp_reqs:
        if exp_req in resume_exp:
            matched_exp_keywords.append(exp_req)
    
    experience_score = len(matched_exp_keywords) / max(len(job_exp_reqs), 1) if job_exp_reqs else 0.5
    
    # 4. Calculate keyword match using TF-IDF and cosine similarity
    resume_text = " ".join([
        " ".join(resume.get("skills", [])),
        " ".join(resume.get("education", [])),
        " ".join([exp.get("description", "") for exp in resume.get("experience", [])])
    ]).lower()
    
    job_text = " ".join([
        job.get("description", ""),
        " ".join(job.get("required_skills", [])),
        " ".join(job.get("preferred_skills", [])),
        " ".join(job.get("education_requirements", [])),
        " ".join(job.get("experience_requirements", []))
    ]).lower()
    
    # Calculate text similarity
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_text])
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        keyword_match_score = max(0, min(cosine_sim, 1.0))  # Ensure score is between 0 and 1
    except:
        # Fallback if vectorization fails (e.g., empty text)
        keyword_match_score = 0.0
    
    # Calculate overall score
    # Weights: Skills 40%, Education 20%, Experience 20%, Keyword match 20%
    overall_score = (
        (skills_score * 0.4) + 
        (education_score * 0.2) + 
        (experience_score * 0.2) + 
        (keyword_match_score * 0.2)
    ) * 100  # Convert to percentage
    
    return {
        "resume_id": resume.get("file_name", "Unknown"),
        "resume_name": resume.get("name", "Unknown"),
        "job_id": job.get("id", "Unknown"),
        "job_title": job.get("title", "Unknown"),
        "overall_score": round(overall_score, 2),
        "skills_score": round(skills_score * 100, 2),
        "education_score": round(education_score * 100, 2),
        "experience_score": round(experience_score * 100, 2),
        "keyword_match_score": round(keyword_match_score * 100, 2),
        "matched_skills": list(matched_skills_set),
        "matched_education": matched_education,
        "matched_experience_keywords": matched_exp_keywords,
        "missing_skills": list(missing_skills)
    }