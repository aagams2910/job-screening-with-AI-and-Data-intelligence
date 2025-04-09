import axios from "axios";
import { Candidate, JobDescriptionType, EmailData } from "@/types";

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: 'http://localhost:6969/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Job {
  title: string;
  description: string;
  keywords: string[];
}

// Legacy functions for backward compatibility
export const fetchJobTitles = async (): Promise<string[]> => {
  try {
    const response = await api.get('/jobs');
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error("Error fetching job titles:", error);
    return [];
  }
};

export const fetchJobDescription = async (jobTitle: string): Promise<JobDescriptionType> => {
  try {
    const response = await api.get(`/job/${encodeURIComponent(jobTitle)}`);
    return {
      title: jobTitle,
      description: response.data.description,
      keywords: response.data.keywords
    };
  } catch (error) {
    console.error(`Error fetching job description for ${jobTitle}:`, error);
    throw error;
  }
};

export const fetchCandidates = async (jobTitle: string): Promise<Candidate[]> => {
  try {
    const response = await api.get(`/candidates/${encodeURIComponent(jobTitle)}`);
    // Handle the new response format which includes candidates and message
    if (response.data && response.data.candidates) {
      // If there's a message, show it as a toast
      if (response.data.message) {
        console.info(response.data.message);
      }
      return response.data.candidates;
    }
    // Fallback for backward compatibility
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error(`Error fetching candidates for ${jobTitle}:`, error);
    throw error;
  }
};

export const sendInterviewEmail = async (emailData: EmailData): Promise<void> => {
  try {
    await api.post('/send-interview-email', {
      candidate_name: emailData.candidateName,
      email: emailData.candidateEmail,
      job_title: emailData.jobTitle,
      dates: [new Date().toISOString().split('T')[0]], // Default to today
      times: [emailData.interviewTime]
    });
  } catch (error) {
    console.error("Error sending interview email:", error);
    throw error;
  }
};

// Modern API service object
export const apiService = {
  // Get all available job titles
  getJobs: async (): Promise<string[]> => {
    const response = await api.get('/jobs');
    return response.data;
  },

  // Get job details by title
  getJobDetails: async (title: string): Promise<Job> => {
    const response = await api.get(`/job/${encodeURIComponent(title)}`);
    return response.data;
  },

  // Get candidates for a job title
  getCandidates: async (jobTitle: string, threshold = 80, boost = 2.5): Promise<Candidate[]> => {
    const response = await api.get(`/candidates/${encodeURIComponent(jobTitle)}`, {
      params: { threshold, boost },
    });
    return response.data;
  },

  // Send interview email
  sendInterviewEmail: async (data: {
    candidate_name: string;
    email: string;
    job_title: string;
    dates: string[];
    times: string[];
  }): Promise<{ success: boolean }> => {
    const response = await api.post('/send-interview-email', data);
    return response.data;
  },

  // Upload resume
  uploadResume: async (file: File): Promise<{ success: boolean; message: string; name: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Add this new method to the apiService object
  sendBulkInterviewEmails: async (candidates: Candidate[], jobTitle: string): Promise<{
    success: boolean;
    results: Array<{candidate_name: string; email: string; success: boolean}>;
    total_sent: number;
    total_failed: number;
  }> => {
    const response = await api.post('/send-bulk-interview-emails', {
      candidates: candidates.map(c => ({
        name: c.name,
        email: c.email
      })),
      job_title: jobTitle
    });
    return response.data;
  },
};
