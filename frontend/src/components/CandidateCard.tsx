import { useState } from "react";
import { Candidate } from "@/types";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Mail, Phone, ChevronDown, ChevronUp, Send, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface CandidateCardProps {
  candidate: Candidate;
  onSendEmail: (candidate: Candidate, interviewTime: string) => void;
}

const CandidateCard = ({ candidate, onSendEmail }: CandidateCardProps) => {
  const [isInterviewOpen, setIsInterviewOpen] = useState(false);
  const [selectedInterviewTime, setSelectedInterviewTime] = useState<string>("");

  const handleSendEmail = () => {
    if (selectedInterviewTime) {
      onSendEmail(candidate, selectedInterviewTime);
    }
  };

  const interviewSlots = candidate.interview_options.dates.flatMap((date) =>
    candidate.interview_options.times.map((time) => ({
      value: `${date} ${time}`,
      date,
      time,
    }))
  );

  return (
    <Card className="group relative overflow-hidden bg-white/70 backdrop-blur-sm border border-slate-200/60 hover:bg-white/80 transition-all duration-300 hover:shadow-lg">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 via-transparent to-purple-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      <div className="absolute inset-[-1px] bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-[inherit] opacity-0 group-hover:opacity-100 blur-md transition-all duration-500"></div>
      <CardContent className="relative p-6 z-10">
        <div className="space-y-6">
          <div className="space-y-2">
            <div className="flex justify-between items-start gap-4">
              <h3 className="text-2xl font-semibold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent group-hover:scale-[1.02] transition-transform duration-300">
                {candidate.name}
              </h3>
              <div className="flex items-center gap-1 bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 rounded-full hover:shadow-md transition-all duration-300">
                <div className="w-2 h-2 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 animate-pulse-ring"></div>
                <span className="text-sm font-medium text-slate-600">{candidate.score}% Match</span>
              </div>
            </div>
            
            <div className="flex flex-col gap-2 text-sm text-slate-500">
              <div className="flex items-center gap-2 group/item hover:text-blue-600 transition-colors duration-200">
                <Mail className="w-4 h-4 group-hover/item:scale-110 transition-transform duration-200" />
                {candidate.email}
              </div>
              {candidate.phone && (
                <div className="flex items-center gap-2 group/item hover:text-blue-600 transition-colors duration-200">
                  <Phone className="w-4 h-4 group-hover/item:scale-110 transition-transform duration-200" />
                  {candidate.phone}
                </div>
              )}
            </div>
          </div>

          <div className="space-y-3">
            <Progress 
              value={candidate.score} 
              className="h-2 bg-gradient-to-r from-blue-100 to-purple-100 overflow-hidden group-hover:shadow-sm transition-shadow duration-300"
              indicatorClassName="bg-gradient-to-r from-blue-600 to-purple-600 animate-shimmer"
            />
          </div>

          <div className="space-y-2">
            <h4 className="font-medium text-slate-700 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-500 animate-bounce-custom" />
              Matched Skills
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {candidate.keywords.map((keyword, index) => (
                <span
                  key={index}
                  className="px-2 py-1 text-xs bg-gradient-to-r from-blue-50 to-purple-50 text-slate-600 rounded-full border border-blue-100/50 hover:shadow-sm transition-all duration-200 hover:border-blue-200/50"
                  style={{
                    animationDelay: `${index * 100}ms`,
                  }}
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>

          <Button
            variant="outline"
            className="w-full group/btn hover:border-blue-200/50 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50"
            onClick={() => setIsInterviewOpen(!isInterviewOpen)}
          >
            {isInterviewOpen ? (
              <ChevronUp className="w-4 h-4 mr-2 group-hover/btn:scale-110 transition-transform duration-200" />
            ) : (
              <ChevronDown className="w-4 h-4 mr-2 group-hover/btn:scale-110 transition-transform duration-200" />
            )}
            {isInterviewOpen ? "Hide Interview Options" : "View Interview Options"}
          </Button>
        </div>

        <div className={cn(
          "space-y-4 pt-4 transition-all duration-300",
          isInterviewOpen ? "opacity-100 max-h-[500px] border-t" : "opacity-0 max-h-0 overflow-hidden"
        )}>
          <div className="w-full">
            <Select onValueChange={setSelectedInterviewTime}>
              <SelectTrigger className="w-full bg-white/70 backdrop-blur-sm border-slate-200/60 hover:shadow-md transition-shadow duration-200">
                <SelectValue placeholder="Select interview time" />
              </SelectTrigger>
              <SelectContent className="bg-white/90 backdrop-blur-sm border-slate-200/60">
                {interviewSlots.map((slot, index) => (
                  <SelectItem 
                    key={index} 
                    value={slot.value}
                    className="hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 transition-colors duration-150 focus:bg-gradient-to-r focus:from-blue-50 focus:to-purple-50"
                  >
                    {`${slot.date} - ${slot.time}`}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <Button 
            className="w-full relative group/send overflow-hidden bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 transform hover:scale-[1.02] transition-all duration-200 shadow-md hover:shadow-xl disabled:opacity-50 disabled:hover:scale-100" 
            onClick={handleSendEmail}
            disabled={!selectedInterviewTime}
          >
            <Send className="w-4 h-4 mr-2 group-hover/send:scale-110 transition-transform duration-200" />
            Send Interview Invitation
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover/send:translate-x-[200%] transition-transform duration-1000"></div>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default CandidateCard;
