import { JobDescriptionType } from "@/types";
import { Card, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { ChevronDown, ChevronUp, Briefcase, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface JobDescriptionProps {
  description: JobDescriptionType;
  isOpen: boolean;
  onToggle: () => void;
}

const JobDescription = ({ description, isOpen, onToggle }: JobDescriptionProps) => {
  return (
    <Card className="bg-white/70 backdrop-blur-sm border border-slate-200/60">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-4 flex-1">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
                <Briefcase className="relative w-6 h-6 text-blue-600" />
              </div>
              <h2 className="text-2xl font-semibold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
                {description.title}
              </h2>
            </div>
            
            <div className={cn(
              "transition-all duration-300 ease-in-out overflow-hidden",
              isOpen ? "max-h-[1000px] opacity-100" : "max-h-0 opacity-0"
            )}>
              <div className="space-y-6 pt-4">
                <p className="text-slate-600 leading-relaxed">
                  {description.description}
                </p>
                <div className="space-y-3">
                  <h3 className="font-medium text-slate-700 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-purple-500" />
                    Required Skills
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {description.keywords.map((keyword, index) => (
                      <span
                        key={index}
                        className="px-3 py-1.5 text-sm bg-gradient-to-r from-blue-50 to-purple-50 text-slate-700 rounded-full border border-blue-100/50 shadow-sm hover:shadow transition-shadow duration-200 hover:border-blue-200/50 cursor-default"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="relative group text-slate-600 hover:text-slate-900 hover:bg-slate-100/50"
          >
            {isOpen ? (
              <ChevronUp className="w-5 h-5 transform transition-transform group-hover:scale-110" />
            ) : (
              <ChevronDown className="w-5 h-5 transform transition-transform group-hover:scale-110" />
            )}
            <span className="sr-only">
              {isOpen ? "Hide description" : "Show description"}
            </span>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default JobDescription;
