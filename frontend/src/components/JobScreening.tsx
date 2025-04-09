import React, { useState, useEffect } from 'react';
import { fetchJobTitles, fetchJobDescription, fetchCandidates, sendInterviewEmail } from '../services/api';
import { JobDescriptionType, Candidate, EmailData } from '../types';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from './ui/select';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Progress } from './ui/progress';
import { toast } from './ui/use-toast';

export const JobScreening: React.FC = () => {
  const [jobTitles, setJobTitles] = useState<string[]>([]);
  const [selectedJob, setSelectedJob] = useState<string>('');
  const [jobDescription, setJobDescription] = useState<JobDescriptionType | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [threshold, setThreshold] = useState<number>(80);
  const [boost, setBoost] = useState<number>(2.5);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const loadJobTitles = async () => {
      try {
        const titles = await fetchJobTitles();
        setJobTitles(titles);
      } catch (err) {
        setError('Failed to load job titles');
        console.error(err);
      }
    };
    loadJobTitles();
  }, []);

  useEffect(() => {
    const loadJobDescription = async () => {
      if (!selectedJob) return;
      setLoading(true);
      try {
        const description = await fetchJobDescription(selectedJob);
        setJobDescription(description);
      } catch (err) {
        setError('Failed to load job description');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadJobDescription();
  }, [selectedJob]);

  useEffect(() => {
    const loadCandidates = async () => {
      if (!selectedJob) return;
      setLoading(true);
      try {
        const candidatesList = await fetchCandidates(selectedJob);
        setCandidates(candidatesList);
      } catch (err) {
        setError('Failed to load candidates');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadCandidates();
  }, [selectedJob]);

  const handleJobSelect = (jobTitle: string) => {
    setSelectedJob(jobTitle);
    setJobDescription(null);
    setCandidates([]);
  };

  const handleSendEmail = async (emailData: EmailData) => {
    try {
      await sendInterviewEmail(emailData);
      toast({
        title: 'Success',
        description: 'Interview email sent successfully!',
      });
    } catch (err) {
      setError('Failed to send interview email');
      console.error(err);
      toast({
        title: 'Error',
        description: 'Failed to send interview email',
        variant: 'destructive',
      });
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Job Screening System with AI and Data</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="space-y-2">
          <Label htmlFor="job-select">Select Job Title</Label>
          <Select value={selectedJob} onValueChange={handleJobSelect}>
            <SelectTrigger id="job-select">
              <SelectValue placeholder="Choose a job title" />
            </SelectTrigger>
            <SelectContent>
              {jobTitles.map((job) => (
                <SelectItem key={job} value={job}>
                  {job}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="threshold">Match Threshold (%)</Label>
          <Input
            id="threshold"
            type="number"
            min="0"
            max="100"
            value={threshold}
            onChange={(e) => setThreshold(Number(e.target.value))}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="boost">Score Boost Factor</Label>
          <Input
            id="boost"
            type="number"
            min="1"
            max="5"
            step="0.1"
            value={boost}
            onChange={(e) => setBoost(Number(e.target.value))}
          />
        </div>
      </div>

      {jobDescription && (
        <Card className="p-4 mb-6">
          <h2 className="text-xl font-semibold mb-2">{jobDescription.title}</h2>
          <p className="text-gray-600 mb-4">{jobDescription.description}</p>
          <div className="flex flex-wrap gap-2">
            {jobDescription.keywords.map((keyword, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {keyword}
              </span>
            ))}
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {candidates.map((candidate) => (
          <Card key={candidate.cv_number} className="p-4">
            <h3 className="text-lg font-semibold mb-2">{candidate.name}</h3>
            <div className="space-y-2">
              <p className="text-sm">
                <span className="font-medium">Email:</span> {candidate.email}
              </p>
              <p className="text-sm">
                <span className="font-medium">Phone:</span> {candidate.phone}
              </p>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>Match Score:</span>
                  <span>{candidate.score}%</span>
                </div>
                <Progress value={candidate.score} />
              </div>
              <div className="flex flex-wrap gap-1">
                {candidate.keywords.map((keyword, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
              <div className="mt-4">
                <h4 className="font-medium mb-2">Interview Options</h4>
                <div className="space-y-2">
                  {candidate.interview_options.dates.map((date, index) => (
                    <div key={index} className="text-sm">
                      <p className="font-medium">{date}</p>
                      <ul className="list-disc list-inside">
                        {candidate.interview_options.times.map((time, timeIndex) => (
                          <li key={timeIndex}>{time}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
              <Button
                className="w-full mt-4"
                onClick={() =>
                  handleSendEmail({
                    candidateId: candidate.cv_number,
                    candidateName: candidate.name,
                    candidateEmail: candidate.email,
                    jobTitle: selectedJob,
                    interviewTime: candidate.interview_options.times[0],
                  })
                }
                disabled={candidate.email === 'Not found'}
              >
                Send Interview Invitation
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};