
from openai import OpenAI
import os

def analyze_skills_gap(resume_text, job_skills, client):
    prompt = f"""
    Analyze the skills gap between the resume and job requirements:
    
    Resume Text: {resume_text}
    Required Skills: {', '.join(job_skills)}
    
    Provide:
    1. Skills Match Percentage
    2. Present Skills
    3. Missing Skills
    4. Recommendations for Skill Development
    """
    
    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Failed to analyze skills gap. Error: {str(e)}"
