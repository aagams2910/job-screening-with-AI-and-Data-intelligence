# Job Screening with AI and Data Intelligence

## Overview
A modern AI-powered job screening system that helps match candidates with job openings using an intuitive React interface. The system leverages natural language processing to analyze resumes and job descriptions, calculating match scores and suggesting optimal interview slots.

## Features
- **Smart CV Analysis**: Extract key information from candidate resumes using AI
- **Intelligent Job Matching**: Parse job descriptions and match with candidate profiles
- **Advanced Scoring**: Dynamic scoring algorithm with adjustable thresholds
- **Real-time Filtering**: Interactive candidate filtering and sorting
- **Automated Interview Scheduling**: Smart interview time slot suggestions
- **Modern UI/UX**: Responsive design with smooth animations and transitions
- **Email Integration**: Automated interview invitation system

## Technology Stack
### Frontend
- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: React Query
- **Animations**: CSS animations & transitions
- **HTTP Client**: Axios

### Backend
- **Runtime**: Python
- **Framework**: Flask with CORS support
- **Database**: SQLite with SQLAlchemy
- **AI/ML**: LangChain for NLP
- **PDF Processing**: PyPDF2
- **Data Processing**: Pandas

## Setup Instructions

### Prerequisites
- Node.js 18+
- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aagams2910/job-screening-with-AI-and-Data-intelligence.git
   cd job-screening-with-AI-and-Data-intelligence
   ```

2. Backend Setup:
   ```bash
   pip install -r requirements.txt
   ```

3. Frontend Setup:
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. Start the backend server:
   ```bash
   python main.py
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

The application will be available at `http://localhost:6969`

## Project Structure
```
.
├── frontend/                # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   ├── types/         # TypeScript types
│   │   └── hooks/         # Custom React hooks
│   └── public/            # Static assets
│
├── backend/
│   ├── main.py           # Flask application
│   ├── database/         # Database models and migrations
│   └── utils/           # Helper functions
│
├── CVs1/                # Resume storage
├── data/               # Application data
└── requirements.txt    # Python dependencies
```

## Key Features Implementation

### Frontend
- Modern, responsive UI with shadcn/ui components
- Real-time candidate filtering and sorting
- Interactive match score visualization
- Smooth animations and transitions
- Dark mode support
- Toast notifications for actions

### Backend
- RESTful API endpoints for all operations
- AI-powered resume analysis
- Smart candidate-job matching algorithm
- Automated email system for interview invitations
- Secure file upload handling


