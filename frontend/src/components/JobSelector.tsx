import { useState, useEffect } from "react";
import { fetchJobTitles } from "../services/api";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Briefcase, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Loader } from "./ui/loader";

interface JobSelectorProps {
  onSelectJob: (jobTitle: string) => void;
}

const JobSelector = ({ onSelectJob }: JobSelectorProps) => {
  const [jobTitles, setJobTitles] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadJobTitles = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const titles = await fetchJobTitles();
        setJobTitles(Array.isArray(titles) ? titles : []);
        
        if (!Array.isArray(titles)) {
          console.warn("Job titles is not an array:", titles);
        }
      } catch (error) {
        console.error("Failed to load job titles", error);
        setError("Failed to load job titles");
        setJobTitles([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadJobTitles();
  }, []);

  return (
    <div className="space-y-2">
      <Label 
        htmlFor="job-title" 
        className="text-sm font-medium text-slate-700 flex items-center gap-2 group"
      >
        <Briefcase className="w-4 h-4 text-blue-600 group-hover:scale-110 transition-transform duration-200" />
        Select Job Title
      </Label>
      <div className="relative">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg blur opacity-20 group-hover:opacity-30 transition duration-1000"></div>
        <Select 
          onValueChange={onSelectJob} 
          disabled={isLoading}
        >
          <SelectTrigger 
            id="job-title" 
            className={cn(
              "w-full bg-white/70 backdrop-blur-sm border-slate-200/60 shadow-sm hover:shadow-md transition-all duration-200",
              isLoading && "animate-pulse"
            )}
          >
            <SelectValue placeholder={
              isLoading ? (
                <div className="flex items-center gap-2 text-slate-500">
                  <Loader variant="dots" size="sm" className="text-blue-600" />
                  <span>Loading job titles...</span>
                </div>
              ) : (
                "Select a job title"
              )
            } />
          </SelectTrigger>
          <SelectContent className="bg-white/90 backdrop-blur-sm border-slate-200/60 shadow-xl">
            {(Array.isArray(jobTitles) ? jobTitles : []).map((title, index) => (
              <SelectItem 
                key={title} 
                value={title}
                className="hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 transition-colors duration-150 focus:bg-gradient-to-r focus:from-blue-50 focus:to-purple-50"
                style={{
                  animationDelay: `${index * 50}ms`,
                  opacity: 0,
                  animation: 'fadeInUp 0.5s ease forwards'
                }}
              >
                {title}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      {error && (
        <div className="flex items-center gap-2 mt-1.5 text-red-500 animate-bounce-custom">
          <AlertCircle className="w-4 h-4" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      <style>
        {`
          @keyframes fadeInUp {
            from {
              opacity: 0;
              transform: translateY(8px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
        `}
      </style>
    </div>
  );
};

export default JobSelector;
