# Job Screening with AI and Data Intelligence

## Overview
This application is an AI-powered job screening system that helps match candidates with job openings based on their resumes. The system uses natural language processing to extract information from CVs and job descriptions, calculates match scores, and suggests suitable interview times.

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
- **Libraries**: PyPDF2, pandas, dotenv

## Setup Instructions

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/job-screening-with-AI-and-Data-intelligence.git
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
- `main.py`: Core application file with the Streamlit UI and main functionality
- `job_description.csv`: Sample job descriptions
- `CVs1/`: Directory containing sample resumes in PDF format
- `.env`: Configuration file for API keys
- `database/`: Contains database schema
- `data/`: Contains the SQLite database file

## Future Enhancements
The project includes several agent modules in the `agents/` directory and utility functions in the `utils/` directory, which are currently not used but could be integrated for more advanced functionality:
- Advanced NLP for resume parsing
- Semantic matching between job descriptions and candidate skills
- More sophisticated candidate scoring and ranking algorithms
- Integration with calendar systems for interview scheduling

## License
MIT License