import os
from flask import Flask, render_template, request
import PyPDF2
import re
from collections import Counter

# Initialize Flask app
app = Flask(__name__)

# Set the folder where uploaded files will be stored
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Allowed file extension check
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return str(e)

# Simple function to extract skills (words) from text
def extract_skills(text):
    # Remove any non-alphabetic characters and split the text into words
    words = re.findall(r'\b\w+\b', text.lower())
    return set(words)

# Calculate match score based on the overlap of skills (words)
def calculate_match_score(resume_skills, jobdesc_skills):
    common_skills = resume_skills.intersection(jobdesc_skills)
    if not jobdesc_skills:
        return 0, common_skills
    score = len(common_skills) / len(jobdesc_skills) * 100
    return round(score, 2), common_skills  # Round to 2 decimal points

# Generate recommendations based on missing skills (show only key skills)
def generate_recommendations(resume_skills, jobdesc_skills):
    missing_skills = jobdesc_skills - resume_skills
    # Sort missing skills based on frequency of importance (could be customized)
    important_skills = list(missing_skills)[:3]  # Get top 3 missing skills
    recommendations = []
    for skill in important_skills:
        if skill == "python":
            recommendations.append("Learn Python through online courses like Codecademy, Coursera, or edX.")
        elif skill == "java":
            recommendations.append("Brush up on Java through tutorials on Udemy or Java documentation.")
        elif skill == "data analysis":
            recommendations.append("Check out Data Science courses on platforms like DataCamp and Kaggle.")
        else:
            recommendations.append(f"Consider improving your knowledge of {skill} with online tutorials or books.")
    return recommendations

@app.route("/", methods=["GET", "POST"])
def index():
    skills = None
    match_score = None
    recommendations = None
    score_warning = False
    
    if request.method == "POST":
        if "resume" not in request.files:
            return "No resume file uploaded", 400

        resume_file = request.files["resume"]
        
        if resume_file.filename == "":
            return "No selected file", 400

        # Save the uploaded resume file
        resume_filename = resume_file.filename
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
        resume_file.save(resume_path)

        # Extract text from the resume
        resume_text = extract_text_from_pdf(resume_path)
        
        # Clean up the uploaded file
        os.remove(resume_path)

        # Get job description from the form (normal text)
        jobdesc_text = request.form["jobdesc"]

        # Extract skills from resume and job description
        resume_skills = extract_skills(resume_text)
        jobdesc_skills = extract_skills(jobdesc_text)
        
        # Calculate match score and recommendations
        match_score, common_skills = calculate_match_score(resume_skills, jobdesc_skills)
        recommendations = generate_recommendations(resume_skills, jobdesc_skills)
        
        skills = list(common_skills)  # Convert set to list for rendering in HTML

        # Check if match score is below 75%
        if match_score < 75:
            score_warning = True

    return render_template("index.html", skills=skills, match_score=match_score, recommendations=recommendations, score_warning=score_warning)

if __name__ == "__main__":
    app.run(debug=True)

    
