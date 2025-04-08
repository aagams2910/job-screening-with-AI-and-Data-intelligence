import streamlit as st
# from agents.recruiting_agent import RecruitingAgent  # Not used in current implementation
import sqlite3
import os
import pandas as pd
import PyPDF2
import re
import datetime
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Print debug information about environment
print("Working Directory:", os.getcwd())
print("Env file exists:", os.path.exists(".env"))

# Load environment variables with explicit encoding and error handling
try:
    # Try UTF-8 first
    if not os.path.exists(".env"):
        raise FileNotFoundError(".env file not found")
        
    with open(".env", "r", encoding="utf-8") as env_file:
        content = env_file.read()
        if not content.strip():
            raise ValueError(".env file is empty")
        logger.info("Successfully read .env file")
    
    load_dotenv(encoding='utf-8', override=True)
    
    # Verify credentials were loaded
    if not all([os.getenv('GMAIL_USER'), os.getenv('GMAIL_APP_PASSWORD')]):
        raise ValueError("Required environment variables not found in .env")
    
    logger.info("Successfully loaded environment variables")
    
except Exception as e:
    logger.error(f"Error loading .env file: {str(e)}")
    logger.error(f"Error type: {type(e).__name__}")
    logger.error(f"Error traceback: {traceback.format_exc()}")
    logger.info("Continuing without environment variables")

# Debug environment variables removed as they were related to email

# Get email credentials from environment variables
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
COMPANY_NAME = os.getenv('COMPANY_NAME', 'Our Company')

# Update the paths for job descriptions and resumes
job_file_path = './job_description.csv'
resume_directory_path = './CVs1'

# Initialize SQLite database
conn = sqlite3.connect('job_screening.db')
cursor = conn.cursor()

# Drop the existing resumes table if it exists
cursor.execute('DROP TABLE IF EXISTS resumes')

# Recreate the resumes table with the updated schema
cursor.execute('''
CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY,
    name TEXT,
    cv_number TEXT,
    keywords TEXT,
    content TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS job_descriptions (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    keywords TEXT
)
''')

conn.commit()

# Function to extract keywords from text
def extract_keywords(text):
    # Convert text to lowercase
    text = text.lower()
    # Remove punctuation and special characters
    text = re.sub(r'[^\w\s]', ' ', text)
    # Split into words
    words = text.split()
    # Remove duplicates and join with commas
    return ', '.join(set(words))

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + " "
    except Exception as e:
        text = f"Error extracting text: {str(e)}"
    return text

# Improved function to extract candidate name from resume text
def extract_candidate_name(text):
    # Try to find a name pattern at the beginning of the text
    lines = text.split('\n')
    for line in lines[:3]:  # Check first few lines
        line = line.strip()
        # If line contains "Name:" or seems like a name (not too long, not too short)
        if "Name:" in line:
            name = line.split("Name:")[-1].strip()
            return name
        elif 2 <= len(line.split()) <= 4 and len(line) < 40 and not any(x in line.lower() for x in ["resume", "cv", "curriculum", "email", "phone", "@"]):
            return line
    
    # If no name found in header, extract first line that looks like a name
    for line in lines:
        if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', line.strip()):
            return line.strip()
    
    # If all else fails, extract first capitalized words that look like a name
    name_match = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', text)
    if name_match:
        return name_match.group(1)
    
    return "Candidate"  # Default fallback

# Improved function to extract contact information from resume text
def extract_contact_info(text):
    # Enhanced regex patterns for email and phone
    email_pattern = r'[\w\.-]+@[\w\.-]+'  # Basic email pattern
    phone_pattern = r'\+?\d[\d\s.-]{8,}\d'  # Enhanced phone pattern
    
    # Extract email and phone
    email = re.search(email_pattern, text)
    phone = re.search(phone_pattern, text)
    
    # Extract name using the improved function
    name = extract_candidate_name(text)
    
    return name, email.group(0) if email else "Not found", phone.group(0) if phone else "Not found"

# Function to remove common stopwords from keywords
def filter_keywords(keywords):
    stopwords = set(['and', 'or', 'the', 'a', 'an', 'in', 'to', 'with', 'for', 'on', 'by', 'of', 'at', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'but', 'if', 'or', 'because', 'so', 'while', 'although', 'nor', 'yet', 'since', 'until', 'unless', 'about', 'above', 'below', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])
    return [word for word in keywords if word not in stopwords]

# Function to generate interview information (without email functionality)
def generate_interview_options(candidate_name, job_title):
    # Generate interview dates (next 7-14 days)
    today = datetime.datetime.now()
    interview_dates = []
    for i in range(7, 15):
        interview_date = today + datetime.timedelta(days=i)
        if interview_date.weekday() < 5:  # Only weekdays
            interview_dates.append(interview_date.strftime("%A, %B %d, %Y"))
    
    # Select 2 random dates
    selected_dates = random.sample(interview_dates, min(2, len(interview_dates)))
    
    # Generate interview times
    interview_times = ["10:00 AM", "11:30 AM", "2:00 PM", "3:30 PM"]
    selected_times = random.sample(interview_times, min(2, len(interview_times)))
    
    return {
        "candidate_name": candidate_name,
        "job_title": job_title,
        "dates": selected_dates,
        "times": selected_times
    }

def get_role_specific_content(job_title):
    """Generate role-specific email content"""
    role_content = {
        "Software Engineer": """
We are particularly impressed with your technical background and would like to discuss your experience in software development.
During the interview, we'll explore your programming skills and problem-solving abilities.""",
        
        "Data Scientist": """
We are excited to discuss your experience in data analysis and machine learning.
The interview will include conversations about your analytical skills and past projects.""",
        
        "Product Manager": """
We look forward to discussing your experience in product development and strategic planning.
The interview will focus on your leadership approach and product vision.""",
        
        "DevOps Engineer": """
We're keen to explore your experience with cloud infrastructure and automation.
The interview will cover your expertise in CI/CD pipelines and infrastructure management."""
    }
    
    return role_content.get(job_title, """
We are impressed with your qualifications and would like to discuss your experience in more detail.
The interview will help us better understand your skills and how they align with our requirements.""")

def send_interview_email(candidate_name, email, job_title, dates, times):
    """Send interview invitation email to candidate"""
    if not all([GMAIL_USER, GMAIL_APP_PASSWORD]):
        logger.warning("Email credentials not found in .env file")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{COMPANY_NAME} HR <{GMAIL_USER}>"
        msg['To'] = email
        msg['Subject'] = f"Interview Invitation for {job_title} Position - {COMPANY_NAME}"
        
        # Get role-specific content
        role_content = get_role_specific_content(job_title)
        
        body = f"""Dear {candidate_name},

Thank you for applying for the {job_title} position at {COMPANY_NAME}. We are pleased to inform you that your profile has been shortlisted for the next round of our hiring process.

{role_content}

We would like to schedule an interview at your convenience. Here are the available slots:

"""
        # Add formatted dates and times
        for date in dates:
            body += f"\nDate: {date}"
            body += "\nAvailable times:"
            for time in times:
                body += f"\n- {time}"
            body += "\n"
        
        body += f"""
Please reply to this email with your preferred slot from the above options. If none of these times work for you, please suggest alternative times that would be more convenient.

Interview Format:
- Duration: 45-60 minutes
- Mode: Video Conference (link will be shared upon confirmation)
- Please have a stable internet connection and a quiet environment

What to Prepare:
1. An updated copy of your resume
2. Any relevant portfolio or work samples
3. Questions you may have about the role or company

Best regards,
HR Team
{COMPANY_NAME}
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session and send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
            logger.info(f"Successfully sent interview invitation to {email}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {str(e)}")
        return False

# Process resumes silently without displaying info messages
def process_resumes_silently():
    cursor.execute("SELECT COUNT(*) FROM resumes")
    resume_count = cursor.fetchone()[0]
    
    # Process and store resumes if not already done
    if resume_count == 0:
        # Get the list of resume files
        resume_files = [f for f in os.listdir(resume_directory_path) if f.endswith('.pdf')]
        
        for resume_file in resume_files:
            # Process resume
            cv_number = resume_file.split('.')[0]
            file_path = os.path.join(resume_directory_path, resume_file)
            content = extract_text_from_pdf(file_path)
            keywords = extract_keywords(content)
            
            # Store in database
            cursor.execute(
                'INSERT INTO resumes (name, cv_number, keywords, content) VALUES (?, ?, ?, ?)',
                (cv_number, cv_number, keywords, content)
            )
        
        conn.commit()

# Process job descriptions silently
def process_job_descriptions_silently():
    cursor.execute("SELECT COUNT(*) FROM job_descriptions")
    job_count = cursor.fetchone()[0]
    
    if job_count == 0:
        # Read job descriptions
        job_df = pd.read_csv(job_file_path, encoding='ISO-8859-1')
        
        for index, row in job_df.iterrows():
            title = row['Job Title']
            description = row['Job Description']
            keywords = extract_keywords(description)
            
            # Store in database
            cursor.execute(
                'INSERT INTO job_descriptions (title, description, keywords) VALUES (?, ?, ?)',
                (title, description, keywords)
            )
        
        conn.commit()

# Process data silently
with st.spinner('Loading data...'):
    process_resumes_silently()
    process_job_descriptions_silently()

# Load job titles from the database
cursor.execute("SELECT title FROM job_descriptions")
job_titles = [row[0] for row in cursor.fetchall()]

# Streamlit UI
st.title("AI-Powered Job Screening System")

# Sidebar for configuration
threshold_score = 80
boost_factor = 2.5

# Job Title Selection
st.header("Select Job Title")
selected_job_title = st.selectbox("Choose a Job Title", job_titles)

# Only show results when button is clicked
show_results = st.button("Find Top Candidates")

if show_results:
    # Retrieve job description and keywords
    cursor.execute('SELECT description, keywords FROM job_descriptions WHERE title = ?', (selected_job_title,))
    result = cursor.fetchone()
    
    if result:
        job_description, job_keywords = result
        job_keywords = job_keywords.split(', ')
        
        st.subheader(f"Selected Job: {selected_job_title}")
        with st.expander("View Job Description"):
            st.write(job_description)
        
        # Match resumes based on keywords
        cursor.execute('SELECT cv_number, keywords, content FROM resumes')
        candidates = cursor.fetchall()
        
        # Match candidates based on keywords
        matched_candidates = []
        for cv_number, candidate_keywords, content in candidates:
            candidate_keywords = candidate_keywords.split(', ')
            # Calculate match score - number of matching keywords
            common_keywords = set(job_keywords) & set(candidate_keywords)
            match_score = len(common_keywords)
            if match_score > 0:
                name, email, phone = extract_contact_info(content)
                filtered_keywords = filter_keywords(common_keywords)
                # Apply higher boost factor for better scores
                normalized_score = int(min(100, (match_score / len(job_keywords)) * 100 * boost_factor))
                matched_candidates.append((cv_number, normalized_score, filtered_keywords, name, email, phone, content))
        
        # Sort candidates by match score
        matched_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Filter candidates by threshold
        shortlisted_candidates = [c for c in matched_candidates if c[1] >= threshold_score]
        
        # Display shortlisted candidates
        st.subheader(f"Top Matching Candidates for {selected_job_title}")
        
        # If no candidates meet the threshold, use the top 10 candidates instead
        if not shortlisted_candidates and matched_candidates:
            st.warning(f"No candidates met the minimum threshold score of {threshold_score}. Showing top 10 candidates instead.")
            shortlisted_candidates = matched_candidates[:10]
        
        if shortlisted_candidates:
            for i, (cv_number, normalized_score, filtered_keywords, name, email, phone, content) in enumerate(shortlisted_candidates):
                st.write(f"**#{i+1}: {name} (ID: {cv_number})**")
                st.write(f"**Email:** {email}")
                st.write(f"**Phone:** {phone}")
                st.write(f"**Match Score:** {normalized_score} out of 100")
                st.write(f"**Matched Keywords:** {', '.join(filtered_keywords)}")
                
                # Display suggested interview times
                with st.expander(f"Suggested Interview Times for {name}"):
                    interview_options = generate_interview_options(name, selected_job_title)
                    st.write(f"**Suggested Dates:**")
                    for date in interview_options["dates"]:
                        st.write(f"- {date}")
                    st.write(f"**Suggested Times:**")
                    for time in interview_options["times"]:
                        st.write(f"- {time}")
                
                # Send interview email
                if email != "Not found":
                    if send_interview_email(name, email, selected_job_title, 
                                         interview_options["dates"], 
                                         interview_options["times"]):
                        st.success(f"Interview invitation sent to {email}")
                    else:
                        st.error(f"Failed to send interview invitation to {email}")
                
                st.write("---")
        else:
            st.write("No candidates found for this job title.")
    else:
        st.write("Job title not found in the database.")

# Close database connection when app is done
conn.close()