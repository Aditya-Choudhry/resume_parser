
def generate_cover_letter(name, skills, job_description):
    prompt = f"""
    Write a professional cover letter for {name} applying for a position with the following details:
    
    Required Skills: {', '.join(skills)}
    
    Job Description: {job_description}
    
    Keep the tone professional but engaging, and highlight how the candidate's skills match the requirements.
    """
    
    try:
        from app import client
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Failed to generate cover letter. Error: {str(e)}"
