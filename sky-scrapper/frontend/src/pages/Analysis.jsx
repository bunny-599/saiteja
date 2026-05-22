import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import ProgressTracker from '../components/ProgressTracker.jsx';
import { AlertCircle, ArrowLeft } from 'lucide-react';

export default function Analysis() {
  const { jobId } = useParams();
  const navigate = useNavigate();

  // Poll status endpoint every 3 seconds
  const { data: job, error, isLoading } = useQuery({
    queryKey: ['jobStatus', jobId],
    queryFn: () => api.getJobStatus(jobId),
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.status === 'complete' || data?.status === 'failed') {
        return false;
      }
      return 3000;
    },
  });

  // Redirect to report view when complete
  useEffect(() => {
    if (job?.status === 'complete') {
      const timer = setTimeout(() => {
        navigate(`/report/${jobId}`);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [job?.status, jobId, navigate]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="w-8 h-8 rounded-full border-2 border-t-teal-500 border-r-transparent border-b-transparent border-l-transparent animate-spin" />
        <span className="text-slate-400 text-sm">Accessing research logs...</span>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="max-w-md mx-auto py-20 px-4 space-y-6 text-center">
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-full w-fit mx-auto">
          <AlertCircle className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <h2 className="text-lg font-bold text-slate-100">Job lookup failed</h2>
          <p className="text-sm text-slate-400">
            {error?.response?.data?.detail || 'The requested analysis job ID does not exist.'}
          </p>
        </div>
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center space-x-2 text-xs font-semibold text-teal-400 hover:text-teal-300 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Dashboard</span>
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
      <ProgressTracker
        status={job.status}
        progress={job.progress}
        logs={job.logs}
        errorLog={job.error_log}
        companyName={job.company_name}
      />
    </div>
  );
}
