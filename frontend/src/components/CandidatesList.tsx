import { useState } from "react";
import { Candidate } from "@/types";
import CandidateCard from "./CandidateCard";
import { Button } from "./ui/button";
import { Mail } from "lucide-react";
import { useToast } from "./ui/use-toast";

interface CandidatesListProps {
  candidates: Candidate[];
  jobTitle: string;
  onSendEmail: (candidate: Candidate, interviewTime: string) => Promise<void>;
}

const CandidatesList = ({ candidates, jobTitle, onSendEmail }: CandidatesListProps) => {
  const { toast } = useToast();
  const [isSendingBulk, setIsSendingBulk] = useState(false);

  const handleBulkEmailSend = async () => {
    try {
      setIsSendingBulk(true);
      const response = await fetch('/api/send-bulk-interview-emails', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          candidates,
          job_title: jobTitle
        }),
      });

      const result = await response.json();
      
      if (result.success) {
        toast({
          title: "Interview Invitations Sent",
          description: `Successfully sent ${result.total_sent} emails. ${result.total_failed} failed.`,
          variant: "default",
        });
      } else {
        throw new Error("Failed to send some emails");
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send interview invitations",
        variant: "destructive",
      });
    } finally {
      setIsSendingBulk(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="bg-white/70 backdrop-blur-sm rounded-xl border border-slate-200/60 p-6 shadow-lg">
        <div className="flex justify-between items-center">
          <div className="space-y-1">
            <h2 className="text-3xl font-bold">
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Top Matched Candidates
              </span>
            </h2>
            <p className="text-slate-500">Found {candidates.length} matching profiles</p>
          </div>
          <Button 
            onClick={handleBulkEmailSend} 
            disabled={isSendingBulk || candidates.length === 0}
            className="relative group overflow-hidden bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg transform hover:scale-105 transition-all duration-200 shadow-md hover:shadow-xl flex items-center gap-2"
          >
            <Mail className="w-4 h-4 transition-transform group-hover:scale-110" />
            {isSendingBulk ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                <span>Sending...</span>
              </div>
            ) : (
              <span>Send All Interview Invitations</span>
            )}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-1000"></div>
          </Button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <style>
          {`
            @keyframes fadeInUp {
              from {
                opacity: 0;
                transform: translateY(20px);
              }
              to {
                opacity: 1;
                transform: translateY(0);
              }
            }
          `}
        </style>
        {candidates.map((candidate, index) => (
          <div
            key={candidate.cv_number}
            className="transform transition-all duration-300"
            style={{
              opacity: 0,
              animation: 'fadeInUp 0.5s ease forwards',
              animationDelay: `${index * 0.1}s`
            }}
          >
            <CandidateCard
              candidate={candidate}
              onSendEmail={onSendEmail}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default CandidatesList;
