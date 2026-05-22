import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { api } from '../api/client';
import { ShieldAlert, Globe, Star, Newspaper, MessageSquare, Landmark, Loader2 } from 'lucide-react';

export default function Home() {
  const navigate = useNavigate();
  const location = useLocation();
  const [companyName, setCompanyName] = useState('');
  const [industry, setIndustry] = useState('');
  const [depth, setDepth] = useState('standard');
  const [errorMsg, setErrorMsg] = useState('');

  const path = location.pathname;
  let jobType = 'analyze';
  if (path === '/marketing') jobType = 'marketing';
  else if (path === '/future') jobType = 'future';

  const config = {
    analyze: {
      badge: 'SWOT & Competitor Engine',
      title: 'Real-time Competitor SWOT Analyzer',
      desc: 'Sky-Scrapper scans the public web in real-time, executing multi-vector scraping pipelines and feeding data to Claude AI to build actionable competitor profiles and SWOT analyses.',
      glowClass: 'glow-teal',
      btnGradient: 'from-teal-500 to-blue-600 hover:from-teal-400 hover:to-blue-500',
      btnGlow: 'glow-teal',
      badgeClass: 'bg-teal-500/10 text-teal-400 border-teal-500/20',
      btnText: 'Initialize SWOT Pipeline',
      steps: [
        { icon: <Globe className="w-5 h-5 text-teal-400" />, title: 'Website Crawling', desc: 'Analyzes tagline, features, and value propositions of company and competitors.' },
        { icon: <Landmark className="w-5 h-5 text-purple-400" />, title: 'Financial Metrics', desc: 'Pulls Growjo revenue estimates, funding rounds, and employee counts.' },
        { icon: <Newspaper className="w-5 h-5 text-pink-400" />, title: 'Google News RSS', desc: 'Aggregates Google News RSS + TechCrunch search for recent PR updates.' },
        { icon: <Star className="w-5 h-5 text-amber-400" />, title: 'Trustpilot Reviews', desc: 'Pulls competitor reviews to feed SWOT analysis quadrants.' }
      ]
    },
    marketing: {
      badge: 'Ads & Sentiment Engine',
      title: 'Marketing & Ads Sentiment Intelligence',
      desc: 'Connects directly with Trustpilot review scraping systems and active social media advertising pipelines to analyze customer satisfaction, NPS, and live ads campaigns.',
      glowClass: 'shadow-[0_0_30px_rgba(59,130,246,0.15)] border-blue-500/40',
      btnGradient: 'from-blue-500 to-indigo-650 hover:from-blue-450 hover:to-indigo-600',
      btnGlow: 'glow-blue',
      badgeClass: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      btnText: 'Initialize Marketing Pipeline',
      steps: [
        { icon: <Star className="w-5 h-5 text-amber-400" />, title: 'Customer Sentiment', desc: 'Pulls Trustpilot customer reviews, calculating rating trends and NPS estimates.' },
        { icon: <MessageSquare className="w-5 h-5 text-blue-400" />, title: 'Meta Ad Placements', desc: 'Queries active campaigns on Facebook and Instagram Ads Library.' },
        { icon: <Globe className="w-5 h-5 text-teal-400" />, title: 'Value Positioning', desc: 'Crawls messaging angles and hooks from landing pages.' },
        { icon: <Newspaper className="w-5 h-5 text-pink-400" />, title: 'Brand Mention Scraping', desc: 'Queries press releases and social mentions for public sentiment.' }
      ]
    },
    future: {
      badge: 'Opportunities & Strategy Engine',
      title: 'Market Gaps & Future Opportunity Strategy',
      desc: 'Processes financial stats, tech stack changes, and market shifts to forecast strategic recommendations, monthly roadmap goals, and competitive defense systems.',
      glowClass: 'shadow-[0_0_30px_rgba(245,158,11,0.15)] border-amber-500/40',
      btnGradient: 'from-amber-500 to-orange-600 hover:from-amber-450 hover:to-orange-550',
      btnGlow: 'hover:shadow-[0_0_20px_rgba(245,158,11,0.3)]',
      badgeClass: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      btnText: 'Initialize Strategy Pipeline',
      steps: [
        { icon: <Landmark className="w-5 h-5 text-purple-400" />, title: 'Financial Metrics', desc: 'Pulls Growjo revenue estimates, funding rounds, and employee counts.' },
        { icon: <Newspaper className="w-5 h-5 text-pink-400" />, title: 'Market Alerts', desc: 'Aggregates Google News RSS + TechCrunch search for recent PR developments.' },
        { icon: <Globe className="w-5 h-5 text-teal-400" />, title: 'Technological Gaps', desc: 'Identifies product tech stacks and scans for tech opportunities.' },
        { icon: <ShieldAlert className="w-5 h-5 text-teal-400" />, title: 'Operational Roadmap', desc: 'Synthesizes weekly priorities and mid-term strategic corporate objectives.' }
      ]
    }
  }[jobType];

  const mutation = useMutation({
    mutationFn: api.submitAnalysis,
    onSuccess: (data) => {
      if (data && data.job_id) {
        navigate(`/analysis/${data.job_id}`);
      }
    },
    onError: (err) => {
      setErrorMsg(err.response?.data?.detail || 'Failed to submit analysis. Please try again.');
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    setErrorMsg('');
    
    if (!companyName.trim() || !industry.trim()) {
      setErrorMsg('Please fill in all required fields.');
      return;
    }
    
    mutation.mutate({
      companyName: companyName.trim(),
      industry: industry.trim(),
      depth,
      jobType
    });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
      {/* Intro details (7 cols) */}
      <div className="lg:col-span-7 space-y-8">
        <div className="space-y-4">
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border uppercase tracking-wider ${config.badgeClass}`}>
            {config.badge}
          </span>
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white leading-[1.1]">
            {config.title.split(' ').slice(0, 2).join(' ')}{' '}
            <span className="bg-gradient-to-r from-teal-400 via-blue-500 to-amber-400 bg-clip-text text-transparent">
              {config.title.split(' ').slice(2, 4).join(' ')}
            </span>{' '}
            {config.title.split(' ').slice(4).join(' ')}
          </h1>
          <p className="text-slate-400 text-lg leading-relaxed max-w-xl">
            {config.desc}
          </p>
        </div>

        {/* Features list */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4">
          {config.steps.map((step, idx) => (
            <div key={idx} className="flex items-start space-x-3.5 bg-slate-900/30 border border-slate-900/80 p-4 rounded-xl">
              <div className="p-2 bg-slate-950 rounded-lg border border-slate-800 shrink-0">
                {step.icon}
              </div>
              <div>
                <h3 className="font-semibold text-sm text-slate-200">{step.title}</h3>
                <p className="text-xs text-slate-500 leading-normal mt-0.5">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Submission Form (5 cols) */}
      <div className="lg:col-span-5">
        <div className={`glass-panel p-6 md:p-8 space-y-6 ${config.glowClass}`}>
          <div className="border-b border-slate-900 pb-4">
            <h2 className="text-xl font-bold text-slate-100">Submit New Analysis</h2>
            <p className="text-xs text-slate-400 mt-1">Specify target company domain or search query.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Company Name */}
            <div className="flex flex-col space-y-1.5">
              <label htmlFor="companyName" className="text-xs font-semibold text-slate-400 uppercase tracking-wider pl-1">
                Company Name / Domain
              </label>
              <input 
                id="companyName"
                type="text" 
                placeholder="e.g. OpenAI or openai.com" 
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                disabled={mutation.isPending}
                className="glass-input"
              />
            </div>

            {/* Industry */}
            <div className="flex flex-col space-y-1.5">
              <label htmlFor="industry" className="text-xs font-semibold text-slate-400 uppercase tracking-wider pl-1">
                Industry Segment
              </label>
              <input 
                id="industry"
                type="text" 
                placeholder="e.g. Artificial Intelligence" 
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                disabled={mutation.isPending}
                className="glass-input"
              />
            </div>

            {/* Depth Selector */}
            <div className="space-y-2">
              <span className="block text-xs font-semibold text-slate-400 uppercase tracking-wider pl-1">
                Analysis Depth
              </span>
              <div className="grid grid-cols-2 gap-3 bg-slate-950 p-1.5 border border-slate-900 rounded-xl">
                <button
                  type="button"
                  onClick={() => setDepth('standard')}
                  disabled={mutation.isPending}
                  className={`py-2 px-3 text-xs font-semibold rounded-lg transition-all ${
                    depth === 'standard' 
                      ? 'bg-slate-900 text-teal-405 border border-slate-800 shadow' 
                      : 'text-slate-400 hover:text-slate-200 border border-transparent'
                  }`}
                >
                  Standard (Top 5 Competitors)
                </button>
                <button
                  type="button"
                  onClick={() => setDepth('deep')}
                  disabled={mutation.isPending}
                  className={`py-2 px-3 text-xs font-semibold rounded-lg transition-all ${
                    depth === 'deep' 
                      ? 'bg-slate-900 text-teal-405 border border-slate-800 shadow' 
                      : 'text-slate-400 hover:text-slate-200 border border-transparent'
                  }`}
                >
                  Deep (Extended Search)
                </button>
              </div>
            </div>

            {/* Error Message */}
            {errorMsg && (
              <div className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/20 p-3 rounded-lg">
                {errorMsg}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={mutation.isPending}
              className={`w-full bg-gradient-to-r py-3.5 rounded-xl font-bold text-sm text-white hover:scale-[1.01] active:scale-[0.99] transition-all flex items-center justify-center space-x-2 disabled:opacity-50 disabled:pointer-events-none ${config.btnGradient} ${config.btnGlow}`}
            >
              {mutation.isPending ? (
                <>
                  <Loader2 className="w-4.5 h-4.5 animate-spin" />
                  <span>Submitting request...</span>
                </>
              ) : (
                <span>{config.btnText}</span>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
