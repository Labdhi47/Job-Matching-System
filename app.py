# app.py

import streamlit as st
import nltk
from job_matcher import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_resume_info,
    parse_job_descriptions,
    match_resume_with_jobs,
)

# Download the NLTK tokenizer data
nltk.download('punkt')

# Streamlit UI setup
st.title("Job Matching System")

# Upload Job Descriptions
job_files = st.file_uploader("Upload Job Descriptions (TEXT or JSON)", type=['txt', 'json'], accept_multiple_files=True)

# Upload Resume
resume_file = st.file_uploader("Upload Candidate Resume (PDF or DOCX)", type=['pdf', 'docx'])

# Function to read file content with error handling for encoding
def read_file_content(file):
    """
    Reads the content of a given file and handles potential encoding issues.

    Args:
        file: The uploaded file object.

    Returns:
        str: The content of the file as a string, or None if decoding fails.
    """
    try:
        return file.read().decode('utf-8')
    except UnicodeDecodeError:
        try:
            return file.read().decode('ISO-8859-1')
        except UnicodeDecodeError:
            st.error("Could not decode the file. Please check the file format and encoding.")
            return None

# Check if both resume and job descriptions are uploaded
if resume_file and job_files:
    # Process the uploaded resume file based on its type
    if resume_file.type == 'application/pdf':
        resume_text = extract_text_from_pdf(resume_file)  # Extract text from PDF
    elif resume_file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        resume_text = extract_text_from_docx(resume_file)  # Extract text from DOCX

    # Extract skills, education, and experience from the resume text
    resume_info = extract_resume_info(resume_text)

    # Read and process job descriptions from the uploaded files
    job_desc_texts = [read_file_content(file) for file in job_files]
    job_descriptions = parse_job_descriptions(job_desc_texts)

    # Match the resume information with the job descriptions
    match_results = match_resume_with_jobs(resume_info, job_descriptions)

    # Determine the best job fit based on skills match percentage
    best_fit = max(match_results, key=lambda x: x['skills_match_percentage'], default=None)

    # Display the results of the best job fit
    if best_fit:
        st.subheader("Best Job Fit")
        st.write(f"**Job Description:** {best_fit['job_description']}")
        st.write(f"**Skills Match Percentage:** {best_fit['skills_match_percentage']:.2f}%")
        st.write(f"**Experience Match:** {'Yes' if best_fit['experience_match'] else 'No'} (Required: {best_fit['total_experience_required']} years)")
        st.write(f"**Education Match:** {'Yes' if best_fit['education_match'] else 'No'}")
else:
    # Warning message if either job descriptions or resume is not uploaded
    st.warning("Please upload job descriptions and a resume.")