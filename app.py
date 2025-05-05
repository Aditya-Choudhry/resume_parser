import streamlit as st
import pdfplumber
from docx import Document
import re
import os
from openai import OpenAI
from dotenv import load_dotenv
from job_scraper import scrape_job_description
from cover_letter import generate_cover_letter

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

# OpenRouter API Configuration
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

# Function to extract text from PDF
def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        return "".join(page.extract_text() or "" for page in pdf.pages)

# Function to extract text from DOCX
def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join(para.text for para in doc.paragraphs)

# Function to extract candidate name and email
def extract_info(text):
    email = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    email = email[0] if email else "Not Found"
    name = text.split('\n')[0].strip()  # Assume first line is the name
    return name, email

# Function to get ATS score using AI
def get_ats_score_with_ai(text, required_skills):
    prompt = f"""
    Evaluate the ATS compatibility of the following resume based on these key criteria:

    Resume Text:
    {text}

    Required Skills:
    {', '.join(required_skills)}

    Analyze and score based on:
    1. Keywords Optimization (20%):
       - Presence of job-specific keywords
       - Natural keyword placement
       - Use of both full terms and abbreviations

    2. Format & Structure (20%):
       - Clear section headings
       - Simple formatting
       - Proper chronological order
       - No complex elements (tables, graphics)

    3. Content Quality (30%):
       - Quantifiable achievements
       - Relevant work experience
       - Education and certifications
       - Skills alignment

    4. Technical Compatibility (15%):
       - Text parsing quality
       - No special characters issues
       - Clean formatting

    5. Contact Information (15%):
       - Completeness
       - Professional presentation
       - Proper placement

    Provide:
    1. Overall ATS Score (0-100%)
    2. Individual category scores
    3. Specific improvements needed
    4. Keywords found vs missing
    """

    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Failed to calculate ATS score. Error: {e}"

# Function to get AI resume improvement suggestions
def get_resume_suggestions(text, required_skills):
    prompt = f"""
    The candidate's resume text is: {text}
    The required skills for the job are: {', '.join(required_skills)}
    Provide suggestions to improve the resume to better match the required skills.
    """

    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Failed to get suggestions. Error: {e}"

def analyze_resume_sections(text, required_skills):
    prompt = f"""
    Analyze the following resume sections and provide a score (0-100) for each major section:

    Resume Text:
    {text}

    Required Skills:
    {', '.join(required_skills)}

    Analyze and score:
    1. Professional Summary/Objective
    2. Work Experience
    3. Skills & Technologies
    4. Education
    5. Projects (if any)

    For each section, provide:
    - Score
    - Specific improvements needed
    """

    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Failed to analyze sections. Error: {e}"

def main():
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton > button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            background-color: #0066cc;
            color: white;
        }
        .upload-box {
            border: 2px dashed #0066cc;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }
        .score-box {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Resume Parser and ATS Score Analyzer")
    st.markdown("---")

    # Job Description Input
    st.subheader("Job Description")
    job_url = st.text_input("Enter Job Posting URL (optional):")
    job_description = ""

    if job_url:
        job_description = scrape_job_description(job_url)
        st.text_area("Scraped Job Description", job_description, height=200)

    manual_job_description = st.text_area("Or Paste Job Description:", height=200)
    if manual_job_description:
        job_description = manual_job_description

    # Two-column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class='upload-box'>
                <h3>📄 Upload Resume</h3>
            </div>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])

    if uploaded_file and job_description:
        # Extract text from the uploaded file
        text = extract_text_from_pdf(uploaded_file) if uploaded_file.name.endswith('.pdf') else extract_text_from_docx(uploaded_file)

        # Extract candidate info
        name, email = extract_info(text)

        # Display extracted info
        st.write("### Resume Summary")
        st.write(f"**Name:** {name}")
        st.write(f"**Email:** {email}")

        # Extract skills from job description
        skills_prompt = f"Extract key required skills from this job description: {job_description}"
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            messages=[{"role": "user", "content": skills_prompt}],
        )
        required_skills = completion.choices[0].message.content.split(',')
        st.write("### Extracted Required Skills")
        st.write(required_skills)

        # Section Analysis
        st.write("### Resume Section Analysis")
        section_analysis = analyze_resume_sections(text, required_skills)
        st.write(section_analysis)

        # ATS Score
        st.write("### Overall ATS Score Analysis")
        ats_analysis = get_ats_score_with_ai(text, required_skills)
        st.write(ats_analysis)

        # Improvement Suggestions
        st.write("### Resume Improvement Suggestions")
        suggestions = get_resume_suggestions(text, required_skills)
        st.write(suggestions)

        # Skills Gap Analysis
        st.write("### Skills Gap Analysis")
        if st.button("Analyze Skills Gap"):
            with st.spinner("Analyzing skills gap..."):
                from skills_analyzer import analyze_skills_gap
                gap_analysis = analyze_skills_gap(text, required_skills, client)
                st.success("Analysis complete!")
                st.markdown(f"""
                    <div class='score-box'>
                        {gap_analysis}
                    </div>
                """, unsafe_allow_html=True)

        # Generate Cover Letter
        st.write("### Cover Letter Generator")
        if st.button("Generate Cover Letter"):
            cover_letter = generate_cover_letter(name, required_skills, job_description)
            st.text_area("Generated Cover Letter", cover_letter, height=400)

            # Download button for cover letter
            st.download_button(
                label="Download Cover Letter",
                data=cover_letter,
                file_name="cover_letter.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()