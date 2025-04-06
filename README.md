# Job Screening with AI and Data Intelligence

## Overview
This application is an AI-powered job screening system that helps match candidates with job openings based on their resumes. The system uses natural language processing to extract information from CVs and job descriptions, calculates match scores, and suggests suitable interview date and time.

## Features
- **CV Processing**: Extract key information from candidate resumes
- **Job Description Analysis**: Parse job descriptions to identify key requirements
- **Matching Algorithm**: Score candidates based on skill and experience match
- **Candidate Shortlisting**: Automatically identify top candidates for each position
- **Interview Suggestions**: Generate suggested interview dates and times

## Technology Stack
- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: SQLite

## Setup Instructions

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/aagams2910/job-screening-with-AI-and-Data-intelligence.git
   cd job-screening-with-AI-and-Data-intelligence
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Data Setup
1. Resume Files: Place candidate PDF resumes in the `CVs1` directory
2. Job Descriptions: Use the existing `job_description.csv` or create your own with the same format

## Usage
1. Run the application:
   ```
   streamlit run main.py
   ```

2. Using the web interface:
   - Select a job title from the dropdown
   - Click "Find Top Candidates" to see matching candidates
   - View suggested interview dates and times for each candidate

## Project Structure
```
.
├── main.py                 # Core application file with Streamlit UI
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables and configuration
├── .gitignore             # Git ignore rules
│
├── CVs1/                  # Directory for candidate resumes
│   └── *.pdf             # PDF resume files
│
├── database/              # Database related files
│   └── schema.sql        # SQL schema definitions
│
├── utils/                 # Utility functions and helpers
│   └── __init__.py       # Utils package initialization
│
├── data/                  # Data storage
│   └── job_screening.db  # SQLite database file
│
└── job_description.csv    # Job listings and descriptions

```

### Key Components
- **Application Core**
  - `main.py`: Main application logic, UI, and screening algorithms
  - `requirements.txt`: Project dependencies
  - `.env`: Configuration settings and API keys

- **Data Storage**
  - `database/`: Database schemas and migrations
  - `data/`: Runtime data storage
  - `job_description.csv`: Job listing data

- **Resume Management**
  - `CVs1/`: Storage for candidate resume PDFs
  - Supports PDF format for resume processing

- **Utilities**
  - `utils/`: Helper functions and shared code
  - Contains reusable components and functions


