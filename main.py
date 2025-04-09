from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
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

# Initialize Flask app
app = Flask(__name__, static_folder='frontend/build', static_url_path='')
# Configure CORS to allow requests from the frontend
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:6969", "http://127.0.0.1:6969"]}})

# Load environment variables
try:
    if not os.path.exists(".env"):
        raise FileNotFoundError(".env file not found")
        
    with open(".env", "r", encoding="utf-8") as env_file:
        content = env_file.read()
        if not content.strip():
            raise ValueError(".env file is empty")
        logger.info("Successfully read .env file")
    
    load_dotenv(encoding='utf-8', override=True)
    
    if not all([os.getenv('GMAIL_USER'), os.getenv('GMAIL_APP_PASSWORD')]):
        raise ValueError("Required environment variables not found in .env")
    
    logger.info("Successfully loaded environment variables")
    
except Exception as e:
    logger.error(f"Error loading .env file: {str(e)}")
    logger.error(f"Error type: {type(e).__name__}")
    logger.error(f"Error traceback: {traceback.format_exc()}")
    logger.info("Continuing without environment variables")

# Get email credentials from environment variables
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
COMPANY_NAME = os.getenv('COMPANY_NAME', 'Our Company')

# Update the paths for job descriptions and resumes
job_file_path = './job_description.csv'
resume_directory_path = './CVs1'

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('job_screening.db')
    cursor = conn.cursor()
    
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
    conn.close()

# Initialize database on startup
init_db()

# Dictionary mapping job titles to their required key skills
job_skills = {
    "Software Engineer": [
        "Python", "Java", "C++", "JavaScript", "SQL", "Git", "Data Structures", "Algorithms",
        "Software Architecture", "System Design", "Web Development", "API Development",
        "Testing", "Debugging", "Problem Solving", "Object-Oriented Programming",
        "Microservices", "DevOps", "Cloud Platforms", "Agile Development",
        "Code Review", "Documentation", "Performance Optimization", "Security Practices"
    ],
    "Data Scientist": [
        "Python", "R", "SQL", "Machine Learning", "Deep Learning", "Statistical Analysis",
        "Data Visualization", "Pandas", "NumPy", "Scikit-learn", "TensorFlow",
        "Big Data Technologies", "Data Mining", "Data Preprocessing", "Feature Engineering",
        "Hypothesis Testing", "A/B Testing", "Regression Analysis", "Classification Models",
        "Time Series Analysis", "NLP", "Computer Vision", "Model Deployment", "Data Ethics"
    ],
    "Product Manager": [
        "Product Strategy", "Market Research", "User Experience", "Agile Methodologies",
        "Product Development", "Stakeholder Management", "Business Analysis", "Data Analytics",
        "Project Management", "Product Roadmapping", "Competitive Analysis", "User Stories",
        "Feature Prioritization", "Product Metrics", "A/B Testing", "Customer Journey Mapping",
        "Product Marketing", "Technical Communication", "Strategic Planning", "Risk Management",
        "Team Leadership", "Budget Planning", "Product Launch", "Customer Development"
    ],
    "Cloud Engineer": [
        "AWS", "Azure", "Google Cloud", "Kubernetes", "Docker", "Terraform",
        "Infrastructure as Code", "Cloud Security", "CI/CD", "Microservices",
        "Load Balancing", "Auto Scaling", "Cloud Monitoring", "Network Architecture",
        "Serverless Computing", "Database Management", "Identity Management", "Cost Optimization",
        "Disaster Recovery", "High Availability", "Cloud Migration", "Container Orchestration",
        "Performance Tuning", "Security Compliance"
    ],
    "Cybersecurity Analyst": [
        "Network Security", "SIEM", "Penetration Testing", "Vulnerability Assessment",
        "Security Protocols", "Incident Response", "Risk Analysis", "Firewall Management",
        "Security Tools", "Compliance Standards", "Encryption", "Authentication Systems",
        "Security Auditing", "Threat Detection", "Malware Analysis", "Digital Forensics",
        "Security Architecture", "Cloud Security", "Ethical Hacking", "Security Frameworks",
        "Access Control", "Security Policies", "Network Monitoring", "Security Awareness"
    ],
    "DevOps Engineer": [
        "Docker", "Kubernetes", "Jenkins", "Git", "AWS/Azure/GCP", "Terraform",
        "Ansible", "CI/CD Pipelines", "Linux Systems", "Shell Scripting",
        "Infrastructure as Code", "Configuration Management", "Monitoring Tools",
        "Log Management", "Performance Tuning", "Security Practices", "Version Control",
        "Network Protocols", "Database Administration", "Cloud Architecture",
        "Automation Scripts", "Container Orchestration", "Microservices", "DevSecOps"
    ],
    "Full Stack Developer": [
        "JavaScript", "TypeScript", "React", "Node.js", "HTML5", "CSS3",
        "SQL/NoSQL Databases", "RESTful APIs", "Git", "Front-end Development",
        "Back-end Development", "Web Security", "UI/UX Principles", "Testing Frameworks",
        "State Management", "API Integration", "Authentication/Authorization", "Web Services",
        "Performance Optimization", "Responsive Design", "Cloud Deployment", "Microservices",
        "Docker", "CI/CD"
    ],
    "Big Data Engineer": [
        "Hadoop", "Spark", "Python", "Scala", "SQL", "NoSQL",
        "Data Pipelines", "ETL", "Kafka", "Cloud Platforms",
        "Distributed Computing", "Data Warehousing", "Data Modeling",
        "Data Security", "Performance Tuning", "Batch Processing",
        "Stream Processing", "Data Integration", "Big Data Tools",
        "Database Design", "Data Governance", "Data Architecture",
        "Machine Learning Pipeline", "Data Quality Management"
    ],
    "AI Researcher": [
        "Machine Learning", "Deep Learning", "Neural Networks", "Natural Language Processing",
        "Computer Vision", "Reinforcement Learning", "Python", "TensorFlow/PyTorch",
        "Research Methodology", "Statistical Analysis", "Algorithm Development",
        "Model Optimization", "Data Preprocessing", "Feature Engineering",
        "Experimental Design", "Scientific Writing", "Mathematics", "Probability Theory",
        "Research Ethics", "Model Evaluation", "Transfer Learning", "AI Ethics",
        "Research Publication", "Literature Review"
    ],
    "Database Administrator": [
        "SQL", "Database Management", "MySQL", "PostgreSQL", "Oracle",
        "MongoDB", "Database Security", "Backup & Recovery", "Performance Tuning",
        "Database Design", "Data Migration", "High Availability", "Disaster Recovery",
        "Index Optimization", "Query Optimization", "Database Monitoring",
        "Security Compliance", "Data Modeling", "Stored Procedures", "Replication",
        "Clustering", "Database Maintenance", "Troubleshooting", "Version Control"
    ],
    "Network Engineer": [
        "TCP/IP", "Routing Protocols", "Network Security", "Cisco Technologies",
        "Juniper Networks", "VPN", "Firewalls", "Network Monitoring",
        "Switch Configuration", "Network Design", "SDN", "Network Troubleshooting",
        "WAN Technologies", "Load Balancing", "Network Performance", "DHCP/DNS",
        "Network Architecture", "Wireless Networks", "Network Automation",
        "Security Protocols", "VoIP", "QoS", "Network Documentation", "Cloud Networking"
    ],
    "Software Architect": [
        "System Design", "Architecture Patterns", "Cloud Computing", "Microservices",
        "Security Architecture", "Scalability", "Performance", "Design Patterns",
        "API Design", "Database Design", "Integration Patterns", "Enterprise Architecture",
        "Technical Leadership", "Solution Architecture", "Distributed Systems",
        "Cloud Migration", "System Integration", "Architecture Modeling",
        "Security Compliance", "Performance Optimization", "Code Review",
        "Documentation", "Technology Strategy", "Risk Assessment"
    ],
    "Blockchain Developer": [
        "Solidity", "Smart Contracts", "Ethereum", "Web3.js", "Blockchain Platforms",
        "Cryptography", "DApps", "Security Protocols", "Distributed Systems",
        "Bitcoin Protocol", "Consensus Mechanisms", "Cryptocurrency", "Hyperledger",
        "Token Standards", "Blockchain Architecture", "P2P Networks",
        "Wallet Integration", "Gas Optimization", "Smart Contract Security",
        "Blockchain Scalability", "DeFi Protocols", "Testing Frameworks",
        "Blockchain Interoperability", "Zero-Knowledge Proofs"
    ],
    "IT Project Manager": [
        "Project Management", "Agile/Scrum", "Risk Management", "Stakeholder Management",
        "Team Leadership", "Budgeting", "Resource Planning", "Communication",
        "Problem Solving", "JIRA", "MS Project", "Change Management",
        "Quality Management", "Cost Control", "Sprint Planning", "Project Documentation",
        "Vendor Management", "Contract Negotiation", "Technical Writing",
        "Performance Metrics", "Process Improvement", "Team Building",
        "Project Scheduling", "Status Reporting"
    ],
    "Business Intelligence Analyst": [
        "SQL", "Data Analysis", "Power BI", "Tableau", "Data Visualization",
        "Statistical Analysis", "ETL Processes", "Reporting Tools", "Business Analytics",
        "Data Modeling", "Dashboard Design", "Excel Advanced", "Data Warehousing",
        "KPI Development", "Business Strategy", "Financial Analysis",
        "Predictive Analytics", "Data Mining", "Market Analysis", "Report Automation",
        "Data Quality", "Database Design", "Data Governance", "Performance Metrics"
    ],
    "Robotics Engineer": [
        "ROS", "C++", "Python", "Computer Vision", "Control Systems",
        "Motion Planning", "Sensor Integration", "AI/ML", "Embedded Systems",
        "Mechanical Design", "Electronics", "Real-time Systems", "Signal Processing",
        "Robot Kinematics", "3D Modeling", "Simulation Tools", "PCB Design",
        "Motor Control", "Path Planning", "Machine Vision", "System Integration",
        "Robot Programming", "Sensor Calibration", "Hardware Testing"
    ],
    "Embedded Systems Engineer": [
        "C/C++", "Microcontrollers", "RTOS", "Embedded Linux", "Hardware Interfaces",
        "Firmware Development", "IoT", "Circuit Design", "Debugging Tools",
        "Digital Signal Processing", "ARM Architecture", "Assembly Language",
        "PCB Design", "Serial Protocols", "Power Management", "Hardware Testing",
        "Device Drivers", "Embedded Security", "Wireless Protocols", "System Integration",
        "Performance Optimization", "Memory Management", "Boot Loaders", "Cross-compilation"
    ],
    "Quality Assurance Engineer": [
        "Test Planning", "Manual Testing", "Automated Testing", "Test Frameworks",
        "Selenium", "JUnit/TestNG", "API Testing", "Performance Testing",
        "Bug Tracking", "SDLC", "Test Cases", "Regression Testing",
        "Load Testing", "Security Testing", "Mobile Testing", "Cross-browser Testing",
        "Test Automation", "Quality Metrics", "User Acceptance Testing", "Code Review",
        "Test Documentation", "CI/CD Integration", "Defect Management", "Test Strategy"
    ],
    "UX/UI Designer": [
        "User Research", "Wireframing", "Prototyping", "Figma", "Adobe XD",
        "Sketch", "UI Design", "Interaction Design", "User Testing",
        "Visual Design", "Information Architecture", "Design Systems",
        "Typography", "Color Theory", "Responsive Design", "Accessibility",
        "Design Thinking", "User Flows", "Usability Testing", "Mobile Design",
        "Design Documentation", "Design Patterns", "Brand Guidelines", "Animation Design"
    ]
}

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
    # Comprehensive stopwords list including common job description terms
    stopwords = set([
        # General stopwords
        'and', 'or', 'the', 'a', 'an', 'in', 'to', 'with', 'for', 'on', 'by', 'of', 'at', 
        'from', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'but', 'if', 'because', 'so', 'while', 'although', 'yet', 'since',
        'about', 'above', 'below', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
        'there', 'when', 'where', 'why', 'how', 'all', 'any', 'each', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'not', 'only', 'own', 'same', 'than', 'too',
        'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now',
        
        # Job description specific stopwords
        'we', 'are', 'looking', 'seeking', 'ideal', 'candidate', 'will', 'must', 'should',
        'required', 'requirements', 'job', 'position', 'company', 'working', 'based',
        'like', 'good', 'great', 'years',
        'excellent', 'very', 'such', 'just', 'also', 'our', 'your', 'their', 'this', 'that',
        
        # Additional common words in job descriptions
        'ability', 'work', 'team', 'skills', 'experience', 'knowledge', 'environment',
        'development', 'design', 'implementation', 'management', 'communication',
        'problem', 'solving', 'solutions', 'quality', 'time', 'project', 'projects',
        'responsibilities', 'qualifications', 'education', 'degree', 'bachelor',
        'master', 'phd', 'certification', 'proficiency', 'proficient', 'familiar',
        'understanding', 'strong', 'minimum', 'preferred', 'plus', 'bonus', 'benefits'
    ])
    
    # Ensure keywords is a list before processing
    if isinstance(keywords, str):
        keywords = keywords.split(', ')
    
    # Filter out stopwords and ensure words meet minimum length
    filtered = []
    for word in keywords:
        word = word.strip().lower()
        if (word not in stopwords and
            len(word) > 2 and  # Avoid very short terms
            not word.isdigit() and  # Remove pure numbers
            not any(char.isdigit() for char in word)):  # Remove terms with numbers
            filtered.append(word)
    
    return filtered

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
We are particularly impressed with your technical background and software development experience.
During the interview, we'll explore your programming skills, system design knowledge, and problem-solving abilities.""",
        
        "Data Scientist": """
We are excited to discuss your experience in data analysis, machine learning, and statistical modeling.
The interview will include discussions about your analytical projects, technical skills, and methodologies.""",
        
        "Product Manager": """
We look forward to discussing your experience in product strategy, market analysis, and user-centric development.
The interview will focus on your leadership approach, product vision, and stakeholder management skills.""",
        
        "Cloud Engineer": """
We're eager to explore your experience with cloud platforms, infrastructure design, and DevOps practices.
The interview will cover cloud architecture, automation, and security implementation strategies.""",
        
        "Cybersecurity Analyst": """
We're keen to discuss your experience in cybersecurity, threat detection, and risk management.
The interview will focus on your technical expertise, incident response strategies, and security best practices.""",

        "DevOps Engineer": """
We're excited to explore your experience with CI/CD, infrastructure automation, and cloud technologies.
The interview will cover your expertise in DevOps practices, tool implementations, and automation strategies.""",
        
        "Full Stack Developer": """
We're looking forward to discussing your full-stack development experience and technical versatility.
The interview will explore your frontend and backend expertise, architecture decisions, and development approaches.""",
        
        "Big Data Engineer": """
We're eager to discuss your experience with big data technologies and distributed systems.
The interview will focus on your data pipeline designs, scalability solutions, and technical implementations.""",
        
        "AI Researcher": """
We're excited to explore your research experience in artificial intelligence and machine learning.
The interview will cover your research methodologies, technical innovations, and practical applications.""",
        
        "Database Administrator": """
We're keen to discuss your database management experience and administration skills.
The interview will focus on your expertise in database optimization, security, and maintenance strategies.""",
        
        "Network Engineer": """
We're looking forward to discussing your network infrastructure and security experience.
The interview will cover network design, implementation strategies, and troubleshooting approaches.""",
        
        "Software Architect": """
We're excited to explore your software architecture experience and system design expertise.
The interview will focus on your architectural decisions, scalability approaches, and technical leadership.""",
        
        "Blockchain Developer": """
We're eager to discuss your blockchain development experience and distributed systems knowledge.
The interview will cover smart contract development, security considerations, and implementation strategies.""",
        
        "IT Project Manager": """
We're looking forward to discussing your project management experience and leadership approach.
The interview will focus on your methodology, team management, and project delivery strategies.""",
        
        "Business Intelligence Analyst": """
We're keen to explore your experience in business analytics and data-driven decision making.
The interview will cover your analytical approaches, visualization techniques, and business impact.""",
        
        "Robotics Engineer": """
We're excited to discuss your robotics engineering experience and technical innovations.
The interview will focus on your hardware-software integration, control systems, and automation solutions.""",
        
        "Embedded Systems Engineer": """
We're looking forward to exploring your embedded systems development experience.
The interview will cover your firmware development, hardware interfaces, and optimization strategies.""",
        
        "Quality Assurance Engineer": """
We're eager to discuss your quality assurance experience and testing methodologies.
The interview will focus on your test automation, quality processes, and debugging approaches.""",
        
        "UX/UI Designer": """
We're excited to explore your user experience design expertise and creative approach.
The interview will cover your design process, user research methodologies, and implementation strategies."""
    }
    
    # If job title not found, return a professional generic message
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

# API Routes
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    conn = sqlite3.connect('job_screening.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM job_descriptions")
    jobs = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(jobs)

@app.route('/api/job/<title>', methods=['GET'])
def get_job_details(title):
    conn = sqlite3.connect('job_screening.db')
    cursor = conn.cursor()
    cursor.execute('SELECT description FROM job_descriptions WHERE title = ?', (title,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        description = result[0]
        # Use predefined skills for the job title, or empty list if title not found
        skills = job_skills.get(title, [])
        return jsonify({
            'title': title,
            'description': description,
            'keywords': skills
        })
    return jsonify({'error': 'Job not found'}), 404

@app.route('/api/candidates/<job_title>', methods=['GET'])
def get_candidates(job_title):
    threshold_score = int(request.args.get('threshold', 70))  # Default threshold changed to 70%
    boost_factor = float(request.args.get('boost', 2.5))
    
    conn = sqlite3.connect('job_screening.db')
    cursor = conn.cursor()
    
    # Get job keywords
    cursor.execute('SELECT keywords FROM job_descriptions WHERE title = ?', (job_title,))
    job_result = cursor.fetchone()
    
    if not job_result:
        conn.close()
        return jsonify({'error': 'Job not found'}), 404
    
    job_keywords = job_result[0].split(', ')
    job_keywords = filter_keywords(job_keywords)  # Filter job keywords
    
    # Get candidates
    cursor.execute('SELECT cv_number, keywords, content FROM resumes')
    candidates = cursor.fetchall()
    
    # Match candidates
    matched_candidates = []
    for cv_number, candidate_keywords, content in candidates:
        candidate_keywords = candidate_keywords.split(', ')
        candidate_keywords = filter_keywords(candidate_keywords)  # Filter candidate keywords
        common_keywords = set(job_keywords) & set(candidate_keywords)
        
        if len(common_keywords) > 0:
            match_score = int(min(100, (len(common_keywords) / len(job_keywords)) * 100 * boost_factor))
            name, email, phone = extract_contact_info(content)
            interview_options = generate_interview_options(name, job_title)
            
            candidate_info = {
                'cv_number': cv_number,
                'name': name,
                'email': email,
                'phone': phone,
                'score': match_score,
                'match_score': match_score,  # Add explicit match_score field
                'keywords': list(common_keywords),
                'matched_keywords': list(common_keywords),
                'interview_options': interview_options
            }
            matched_candidates.append(candidate_info)
    
    # Sort by score and get top candidates
    matched_candidates.sort(key=lambda x: x['score'], reverse=True)
    
    # Filter candidates based on threshold
    candidates_above_threshold = [c for c in matched_candidates if c['score'] >= threshold_score]
    
    # Prepare response
    response = {}
    
    if candidates_above_threshold:
        # Return all candidates that meet the threshold
        response['candidates'] = candidates_above_threshold
        response['message'] = f"Found {len(candidates_above_threshold)} candidates that meet or exceed the {threshold_score}% threshold."
    else:
        # If no candidates meet the threshold, return top 5 with a message
        top_5_candidates = matched_candidates[:5] if matched_candidates else []
        response['candidates'] = top_5_candidates
        response['message'] = f"No candidates passed the {threshold_score}% threshold. Returning the top {len(top_5_candidates)} candidates."
    
    conn.close()
    return jsonify(response)

@app.route('/api/send-interview-email', methods=['POST'])
def send_interview_email_route():
    data = request.json
    success = send_interview_email(
        data['candidate_name'],
        data['email'],
        data['job_title'],
        data['dates'],
        data['times']
    )
    return jsonify({'success': success})

@app.route('/api/send-bulk-interview-emails', methods=['POST'])
def send_bulk_interview_emails():
    data = request.json
    candidates = data.get('candidates', [])
    job_title = data.get('job_title')
    
    results = []
    for candidate in candidates:
        # Generate unique interview options for each candidate
        interview_options = generate_interview_options(candidate['name'], job_title)
        
        # Send email with the generated options
        success = send_interview_email(
            candidate['name'],
            candidate['email'],
            job_title,
            interview_options['dates'],
            interview_options['times']
        )
        
        results.append({
            'candidate_name': candidate['name'],
            'email': candidate['email'],
            'success': success
        })
    
    # Return summary of email sending results
    return jsonify({
        'success': True,
        'results': results,
        'total_sent': len([r for r in results if r['success']]),
        'total_failed': len([r for r in results if not r['success']])
    })

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        # Save the file temporarily
        temp_path = os.path.join(resume_directory_path, file.filename)
        file.save(temp_path)
        
        # Process the resume
        content = extract_text_from_pdf(temp_path)
        keywords = extract_keywords(content)
        name = extract_candidate_name(content)
        
        # Store in database
        conn = sqlite3.connect('job_screening.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO resumes (name, cv_number, keywords, content) VALUES (?, ?, ?, ?)',
            (name, file.filename.split('.')[0], keywords, content)
        )
        conn.commit()
        conn.close()
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'message': 'Resume processed successfully',
            'name': name
        })
        
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969, debug=True)