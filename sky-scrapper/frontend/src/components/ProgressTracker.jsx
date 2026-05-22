import { useEffect, useRef } from 'react';
import { Terminal, Shield, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react';

export default function ProgressTracker({ status, progress, logs, errorLog, companyName }) {
  const logEndRef = useRef(null);

  // Scroll to bottom of logs on new message
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const stages = [
    { key: 'discovering', label: 'Discovering' },
    { key: 'scraping', label: 'Scraping' },
    { key: 'analyzing', label: 'Analyzing' },
    { key: 'complete', label: 'Complete' }
  ];

  const getStageIndex = (currentStatus) => {
    if (currentStatus === 'failed') return -1;
    if (currentStatus === 'pending') return 0;
    return stages.findIndex(s => s.key === currentStatus);
  };

  const currentStageIndex = getStageIndex(status);

  return (
    <div className="max-w-4xl mx-auto w-full glass-panel glow-teal p-6 md:p-8 space-y-8">
      {/* Target Title */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-teal-400 to-blue-500 bg-clip-text text-transparent">
          Analyzing {companyName}
        </h2>
        <p className="text-slate-400 text-sm">
          Please wait while the platform crawls live data and calls Claude AI models.
        </p>
      </div>

      {/* Progress Bar & Stages */}
      <div className="relative">
        <div className="flex justify-between items-center mb-6">
          {stages.map((stage, idx) => {
            const isCompleted = currentStageIndex > idx || status === 'complete';
            const isActive = currentStageIndex === idx && status !== 'failed';
            return (
              <div key={stage.key} className="flex flex-col items-center flex-1 relative z-10">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center border text-xs font-semibold transition-all duration-500 ${
                  isCompleted ? 'bg-teal-500 border-teal-400 text-slate-950' : 
                  isActive ? 'bg-blue-600 border-blue-400 text-white animate-pulse-glow' : 
                  'bg-slate-950 border-slate-800 text-slate-500'
                }`}>
                  {isCompleted ? <CheckCircle2 className="w-5 h-5 stroke-[2.5]" /> : idx + 1}
                </div>
                <span className={`text-[11px] font-medium uppercase tracking-wider mt-2.5 ${
                  isActive ? 'text-teal-400' : isCompleted ? 'text-slate-300' : 'text-slate-500'
                }`}>
                  {stage.label}
                </span>
              </div>
            );
          })}
        </div>
        
        {/* Progress Bar track */}
        <div className="absolute top-4 left-[12%] right-[12%] h-[2px] bg-slate-800 -z-0">
          <div 
            className="h-full bg-gradient-to-r from-teal-500 to-blue-500 shadow-[0_0_8px_rgba(20,184,166,0.5)] transition-all duration-500" 
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Numerical percentage indicator */}
      <div className="flex items-center justify-between text-xs text-slate-400 bg-slate-950/60 rounded-xl px-4 py-2 border border-slate-900">
        <span className="flex items-center space-x-2">
          {status !== 'complete' && status !== 'failed' && (
            <Loader2 className="w-3.5 h-3.5 text-teal-400 animate-spin" />
          )}
          <span>Status: <strong className="text-slate-200 capitalize">{status}</strong></span>
        </span>
        <span>Progress: <strong>{progress}%</strong></span>
      </div>

      {/* Logs Console Feed */}
      <div className="space-y-3">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400 uppercase tracking-wider pl-1">
          <Terminal className="w-4 h-4 text-teal-500" />
          <span>Execution logs console</span>
        </div>
        <div className="bg-slate-950/90 border border-slate-900 rounded-xl p-4 font-mono text-[11px] text-teal-500/90 h-64 overflow-y-auto space-y-2.5 shadow-inner">
          {logs && logs.length > 0 ? (
            logs.map((log, idx) => (
              <div key={idx} className="flex items-start space-x-2 hover:bg-slate-900/40 p-1 rounded transition-colors">
                <span className="text-slate-600 shrink-0">[{log.time}]</span>
                <span className="text-teal-400/80 shrink-0">✓</span>
                <span className="text-slate-300 leading-normal">{log.message}</span>
              </div>
            ))
          ) : (
            <div className="text-slate-600 text-center py-20">Initializing terminal feed...</div>
          )}
          {status === 'failed' && (
            <div className="flex items-start space-x-2 text-red-400/90 border-t border-red-950/30 pt-3">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold">CRITICAL FAILURE ERROR:</span>
                <p className="mt-1 text-slate-400 whitespace-pre-wrap">{errorLog}</p>
              </div>
            </div>
          )}
          <div ref={logEndRef} />
        </div>
      </div>
    </div>
  );
}
