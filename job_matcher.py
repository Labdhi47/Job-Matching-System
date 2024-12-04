# job_matcher.py

import json
import re
import pdfplumber
from docx import Document
import spacy

# Function to extract text from PDF files
def extract_text_from_pdf(file):
    """
    Extracts text from a PDF file.

    Args:
        file (str): The path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    with pdfplumber.open(file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    return text

# Function to extract text from DOCX files
def extract_text_from_docx(file):
    """
    Extracts text from a DOCX file.

    Args:
        file (str): The path to the DOCX file.

    Returns:
        str: Extracted text from the DOCX.
    """
    doc = Document(file)
    return '\n'.join([para.text for para in doc.paragraphs])

# Load the English NLP model from spaCy
nlp = spacy.load('en_core_web_sm')

# Function to extract skills, education, and experience from a resume text
def extract_resume_info(resume_text):
    """
    Extracts skills, education, and total experience from resume text.

    Args:
        resume_text (str): The text of the resume.

    Returns:
        dict: A dictionary containing:
            - 'skills': List of unique skills extracted from the resume.
            - 'education': List of educational qualifications found in the resume.
            - 'total_experience': Total years of experience calculated from the resume.
    """
    # Process the resume text with spaCy
    doc = nlp(resume_text)

    # Extract skills (assuming skills are nouns or proper nouns)
    skills = set()
    for token in doc:
        # Add nouns and proper nouns to the skills set
        if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 1:  # Ignore single character tokens
            skills.add(token.text)

    # Extract education qualifications
    education_keywords = {'Bachelor', 'Master', 'PhD', 'Associate', 'Degree', 'Certification'}
    education = set()
    for token in doc:
        if token.text in education_keywords:
            education.add(token.text)

    # Extract experience using regex
    experience = re.findall(r'(\d+)\s+(years?|months?)\s+(of|in)?\s*([A-Za-z\s]+)', resume_text)
    experience_years = sum(int(exp[0]) for exp in experience if 'year' in exp[1].lower())
    experience_months = sum(int(exp[0]) for exp in experience if 'month' in exp[1].lower())
    total_experience = experience_years + experience_months / 12  # Convert months to years

    return {
        'skills': list(skills),  # Unique skills
        'education': list(education),
        'total_experience': total_experience
    }

# Function to parse job descriptions from provided text
def parse_job_descriptions(job_desc_texts):
    """
    Parses job descriptions from a list of text inputs.

    Args:
        job_desc_texts (list): List of job description texts (can be JSON strings).

    Returns:
        list: A list of dictionaries containing parsed job descriptions, requirements,
              experience required, education required, and job titles.
    """
    job_descriptions = []
    for text in job_desc_texts:
        # Load job description from JSON if applicable
        job_desc = json.loads(text) if text.endswith('.json') else {'description': text}
        job_title = job_desc.get('title', 'N/A')
        job_descriptions.append({
            'description': job_desc.get('description', ''),
            'requirements': re.findall(r'\b\w+\b', job_desc.get('description', '')),
            'experience_required': re.findall(r'(\d+)\s+(years?|months?)', job_desc.get('description', '')),
            'education_required': re.findall(r'\b(Bachelor|Master|PhD|Associate|Degree|Certification)\b',
                                             job_desc.get('description', re.I)),
            'job_title': job_title
        })
    return job_descriptions

# Function to match a resume with job descriptions
def match_resume_with_jobs(resume_info, job_descriptions):
    """
    Matches a resume's extracted information with a list of job descriptions.

    Args:
        resume_info (dict): A dictionary containing skills, education, and total experience from the resume.
        job_descriptions (list): A list of dictionaries representing job descriptions.

    Returns:
        list: A list of dictionaries containing match results for each job, including:
            - 'job_title - 'job_title': The title of the job.
            - 'job_description': The description of the job.
            - 'skills_match_percentage': The percentage of skills matched between the resume and job requirements.
            - 'experience_match': A boolean indicating if the resume meets the experience requirements.
            - 'education_match': A boolean indicating if the resume meets the education requirements.
            - 'total_experience_required': The total experience required for the job.
    """
    results = []
    for job in job_descriptions:
        job_skills = job['requirements']
        skills_match = len(set(resume_info['skills']).intersection(set(job_skills)))
        total_skills = len(job_skills)
        match_percentage = (skills_match / total_skills) * 100 if total_skills > 0 else 0

        experience_required = sum(int(exp[0]) for exp in job['experience_required']) if job['experience_required'] else 0
        experience_match = resume_info['total_experience'] >= experience_required
        education_match = any(edu in resume_info['education'] for edu in job['education_required'])

        results.append({
            'job_title': job['job_title'],
            'job_description': job['description'],
            'skills_match_percentage': match_percentage,
            'experience_match': experience_match,
            'education_match': education_match,
            'total_experience_required': experience_required
        })
    return results
