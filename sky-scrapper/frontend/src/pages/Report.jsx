import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import SWOTMatrix from '../components/SWOTMatrix';
import CompetitorCard from '../components/CompetitorCard';
import SentimentChart from '../components/SentimentChart';
import AdsGallery from '../components/AdsGallery';
import MetricsGrid from '../components/MetricsGrid';
import { 
  FileText, Download, Briefcase, RefreshCw, BarChart2, ShieldAlert, 
  Users, MessageSquare, Megaphone, Lightbulb, MapPin, Calendar, Globe, Compass 
} from 'lucide-react';


export default function Report() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [recTab, setRecTab] = useState('weekly');

  const { data: report, error, isLoading, refetch } = useQuery({
    queryKey: ['report', jobId],
    queryFn: () => api.getReport(jobId),
  });

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="w-8 h-8 rounded-full border-2 border-t-teal-500 border-r-transparent border-b-transparent border-l-transparent animate-spin" />
        <span className="text-slate-400 text-sm">Aggregating competitor matrices...</span>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-md mx-auto py-20 px-4 space-y-6 text-center">
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-full w-fit mx-auto">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <h2 className="text-lg font-bold text-slate-100">Failed to load report</h2>
          <p className="text-sm text-slate-400">
            {error?.response?.data?.detail || 'The report data could not be retrieved.'}
          </p>
        </div>
        <button
          onClick={() => navigate('/')}
          className="bg-slate-900 border border-slate-800 text-slate-300 px-5 py-2.5 rounded-xl hover:bg-slate-850 hover:text-white transition-all text-xs font-semibold"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  const { 
    metadata, 
    target_company, 
    competitor_data = [], 
    competitor_profiles = [], 
    swot = {}, 
    sentiment = {}, 
    ads_analysis = {}, 
    market_opportunity = {}, 
    recommendations = {} 
  } = report;

  const jobType = metadata?.job_type || 'analyze';

  const allTabs = [
    { id: 'dashboard', label: 'Overview & Metrics', icon: <BarChart2 className="w-4 h-4" />, visible: true },
    { id: 'competitors', label: 'Competitor Profiling', icon: <Users className="w-4 h-4" />, visible: jobType === 'analyze' },
    { id: 'swot', label: 'SWOT Matrix', icon: <ShieldAlert className="w-4 h-4" />, visible: jobType === 'analyze' },
    { id: 'sentiment', label: 'Customer Sentiment', icon: <MessageSquare className="w-4 h-4" />, visible: jobType === 'marketing' },
    { id: 'ads', label: 'Ad Intelligence', icon: <Megaphone className="w-4 h-4" />, visible: jobType === 'marketing' },
    { id: 'opportunities', label: 'Opportunities', icon: <Lightbulb className="w-4 h-4" />, visible: jobType === 'future' },
    { id: 'recommendations', label: 'Strategic Plan', icon: <FileText className="w-4 h-4" />, visible: jobType === 'future' }
  ];

  const tabs = allTabs.filter(tab => tab.visible);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Report Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 gap-6">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              {target_company.name}
            </h1>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-teal-500/10 text-teal-400 border border-teal-500/20">
              {metadata.industry}
            </span>
          </div>
          {target_company.tagline && (
            <p className="text-slate-400 text-sm italic">"{target_company.tagline}"</p>
          )}
          
          <div className="flex flex-wrap gap-4 text-xs text-slate-500 font-medium">
            <span className="flex items-center space-x-1">
              <Calendar className="w-3.5 h-3.5" />
              <span>Analyzed: {new Date(metadata.analysis_date).toLocaleDateString()}</span>
            </span>
            <span className="flex items-center space-x-1">
              <Globe className="w-3.5 h-3.5" />
              <a href={`https://${target_company.domain}`} target="_blank" rel="noopener noreferrer" className="hover:text-teal-400 transition-colors">
                {target_company.domain}
              </a>
            </span>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center space-x-3 shrink-0">
          <a
            href={api.getPdfDownloadUrl(jobId)}
            className="flex items-center space-x-2 bg-gradient-to-r from-teal-500 to-blue-600 hover:from-teal-400 hover:to-blue-500 text-white px-5 py-3 rounded-xl text-xs font-bold glow-teal transition-all hover:scale-[1.01]"
          >
            <Download className="w-4 h-4" />
            <span>Download PDF Report</span>
          </a>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex flex-wrap gap-2 border-b border-slate-900 pb-px overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center space-x-2 py-3 px-4 text-xs font-semibold transition-all border-b-2 -mb-px outline-none ${
              activeTab === tab.id 
                ? 'border-teal-500 text-teal-400' 
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Contents */}
      <div className="mt-8">
        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            {/* Overview / Tagline Details */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
              {/* Value prop (8 cols) */}
              <div className="md:col-span-8 glass-panel p-6 space-y-4">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest pl-1">
                  Target Value Proposition
                </h3>
                <p className="text-slate-300 text-base leading-relaxed">
                  {target_company.value_proposition || 'No detailed value proposition extracted.'}
                </p>
                
                {target_company.detected_tech_stack && target_company.detected_tech_stack.length > 0 && (
                  <div className="space-y-2 pt-2">
                    <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider pl-1">
                      Target Tech Stack Indicators
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {target_company.detected_tech_stack.map((tech) => (
                        <span 
                          key={tech} 
                          className="px-2.5 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-900 text-xs font-medium"
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Quick Info (4 cols) */}
              <div className="md:col-span-4 glass-panel p-6 space-y-4 flex flex-col justify-center">
                <div className="space-y-3">
                  <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider pl-1">
                    Scraping Resource Usage
                  </span>
                  <div className="space-y-2.5 text-xs text-slate-300">
                    <div className="flex justify-between">
                      <span>Serper API calls:</span>
                      <strong className="text-slate-100">{metadata.quota_usage?.serper_calls || 0}</strong>
                    </div>
                    <div className="flex justify-between">
                      <span>ScraperAPI calls:</span>
                      <strong className="text-slate-100">{metadata.quota_usage?.scraperapi_calls || 0}</strong>
                    </div>
                    <div className="flex justify-between">
                      <span>Direct crawls:</span>
                      <strong className="text-slate-100">{metadata.quota_usage?.direct_scrapes || 0}</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Financial Metrics */}
            <MetricsGrid 
              targetCompany={target_company} 
              competitors={competitor_data} 
            />

            {/* Target News Feed */}
            {target_company.news && target_company.news.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-sm font-bold text-slate-300 flex items-center space-x-2 pl-1">
                  <FileText className="w-4.5 h-4.5 text-teal-400" />
                  <span>Target Press Coverage & News</span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {target_company.news.slice(0, 4).map((n, idx) => (
                    <div key={idx} className="glass-card p-5 space-y-3 flex flex-col justify-between">
                      <div className="space-y-2">
                        <div className="flex justify-between items-center text-[10px] font-semibold text-slate-500">
                          <span>{n.source}</span>
                          <span>{n.date}</span>
                        </div>
                        <h4 className="text-sm font-bold text-slate-200 line-clamp-2">
                          <a href={n.url} target="_blank" rel="noopener noreferrer" className="hover:text-teal-400 transition-colors">
                            {n.headline}
                          </a>
                        </h4>
                        <p className="text-xs text-slate-400 leading-normal">{n.summary}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'competitors' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {competitor_profiles && competitor_profiles.length > 0 ? (
              competitor_profiles.map((profile, idx) => {
                const name = profile.company;
                const raw = competitor_data.find(c => c.name.toLowerCase() === name.toLowerCase()) || competitor_data[idx];
                return (
                  <CompetitorCard 
                    key={idx} 
                    profile={profile} 
                    rawData={raw} 
                  />
                );
              })
            ) : (
              <div className="lg:col-span-2 text-center text-slate-500 py-20 italic">
                No competitor profiles compiled.
              </div>
            )}
          </div>
        )}

        {activeTab === 'swot' && (
          <SWOTMatrix swot={swot} />
        )}

        {activeTab === 'sentiment' && (
          <SentimentChart sentiment={sentiment} />
        )}

        {activeTab === 'ads' && (
          <AdsGallery adsAnalysis={ads_analysis} rawCompetitors={competitor_data} />
        )}

        {activeTab === 'opportunities' && (
          <div className="space-y-6">
            {/* Header */}
            <div>
              <h2 className="text-xl font-bold text-slate-100">Market Opportunities Analysis</h2>
              <p className="text-slate-400 text-xs mt-1">
                Strategic gaps, underserved sectors, and key market growth directions.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* Trends & Segments (5 cols) */}
              <div className="lg:col-span-5 space-y-6">
                <div className="glass-card p-5 space-y-4">
                  <h3 className="text-sm font-bold text-teal-400 flex items-center space-x-2 border-b border-slate-900 pb-2">
                    <Compass className="w-4 h-4" />
                    <span>Emerging Industry Trends</span>
                  </h3>
                  <ul className="space-y-2.5">
                    {market_opportunity.emerging_trends && market_opportunity.emerging_trends.map((t, idx) => (
                      <li key={idx} className="text-xs text-slate-350 leading-relaxed flex items-start space-x-2">
                        <span className="text-teal-500 font-bold shrink-0">•</span>
                        <span>{t}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="glass-card p-5 space-y-4">
                  <h3 className="text-sm font-bold text-blue-400 flex items-center space-x-2 border-b border-slate-900 pb-2">
                    <Users className="w-4 h-4" />
                    <span>Underserved Market Segments</span>
                  </h3>
                  <ul className="space-y-2.5">
                    {market_opportunity.underserved_segments && market_opportunity.underserved_segments.map((s, idx) => (
                      <li key={idx} className="text-xs text-slate-350 leading-relaxed flex items-start space-x-2">
                        <span className="text-blue-500 font-bold shrink-0">•</span>
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Opportunities list (7 cols) */}
              <div className="lg:col-span-7 glass-card p-5 space-y-5">
                <h3 className="text-sm font-bold text-slate-200 border-b border-slate-900 pb-2">
                  Top Recommended Initiatives
                </h3>
                
                <div className="space-y-4 max-h-[460px] overflow-y-auto pr-1">
                  {market_opportunity.top_opportunities && market_opportunity.top_opportunities.map((opp, idx) => {
                    const getUrgencyColor = (urg) => {
                      if (urg?.toLowerCase() === 'high') return 'bg-rose-500/10 text-rose-450 border-rose-500/20';
                      if (urg?.toLowerCase() === 'medium') return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
                      return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
                    };
                    return (
                      <div key={idx} className="bg-slate-950/60 border border-slate-900 p-4 rounded-xl space-y-2.5">
                        <div className="flex justify-between items-center">
                          <strong className="text-sm text-slate-200">{opp.title}</strong>
                          <span className={`text-[9px] font-bold border px-2 py-0.5 rounded uppercase tracking-wider ${getUrgencyColor(opp.urgency)}`}>
                            {opp.urgency} Urgency
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{opp.rationale}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'recommendations' && (
          <div className="space-y-8">
            {/* Header */}
            <div>
              <h2 className="text-xl font-bold text-slate-100">Strategic Recommendations Roadmap</h2>
              <p className="text-slate-400 text-xs mt-1">
                Consultant-grade strategic priorities categorized by business operational segments.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              {/* Tabs sidebar (4 cols) */}
              <div className="lg:col-span-4 flex flex-col space-y-2 bg-slate-950/40 p-2.5 border border-slate-900 rounded-2xl">
                <button
                  onClick={() => setRecTab('weekly')}
                  className={`py-3 px-4 text-left text-xs font-semibold rounded-xl transition-all ${
                    recTab === 'weekly' 
                      ? 'bg-slate-900 text-teal-400 border border-slate-800' 
                      : 'text-slate-450 hover:text-slate-200 border border-transparent'
                  }`}
                >
                  Weekly Priorities (Quick Wins)
                </button>
                <button
                  onClick={() => setRecTab('monthly')}
                  className={`py-3 px-4 text-left text-xs font-semibold rounded-xl transition-all ${
                    recTab === 'monthly' 
                      ? 'bg-slate-900 text-teal-400 border border-slate-800' 
                      : 'text-slate-450 hover:text-slate-200 border border-transparent'
                  }`}
                >
                  Monthly Goals (Mid-Term)
                </button>
                <button
                  onClick={() => setRecTab('marketing')}
                  className={`py-3 px-4 text-left text-xs font-semibold rounded-xl transition-all ${
                    recTab === 'marketing' 
                      ? 'bg-slate-900 text-teal-400 border border-slate-800' 
                      : 'text-slate-450 hover:text-slate-200 border border-transparent'
                  }`}
                >
                  Marketing Initiatives
                </button>
                <button
                  onClick={() => setRecTab('product')}
                  className={`py-3 px-4 text-left text-xs font-semibold rounded-xl transition-all ${
                    recTab === 'product' 
                      ? 'bg-slate-900 text-teal-400 border border-slate-800' 
                      : 'text-slate-450 hover:text-slate-200 border border-transparent'
                  }`}
                >
                  Product Strategy
                </button>
                <button
                  onClick={() => setRecTab('competitive')}
                  className={`py-3 px-4 text-left text-xs font-semibold rounded-xl transition-all ${
                    recTab === 'competitive' 
                      ? 'bg-slate-900 text-teal-400 border border-slate-800' 
                      : 'text-slate-450 hover:text-slate-200 border border-transparent'
                  }`}
                >
                  Competitive Defense Plan
                </button>
              </div>

              {/* Tab Display Panel (8 cols) */}
              <div className="lg:col-span-8 glass-panel p-6 min-h-[300px]">
                {recTab === 'weekly' && (
                  <div className="space-y-4">
                    <h3 className="text-sm font-bold text-teal-450 border-b border-slate-900 pb-2">Weekly Priorities</h3>
                    <ul className="space-y-3">
                      {recommendations.weekly_priorities && recommendations.weekly_priorities.map((item, idx) => (
                        <li key={idx} className="text-xs text-slate-300 leading-normal flex items-start space-x-2">
                          <span className="text-teal-500 font-bold shrink-0">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {recTab === 'monthly' && (
                  <div className="space-y-4">
                    <h3 className="text-sm font-bold text-teal-450 border-b border-slate-900 pb-2">Monthly Goals</h3>
                    <ul className="space-y-3">
                      {recommendations.monthly_goals && recommendations.monthly_goals.map((item, idx) => (
                        <li key={idx} className="text-xs text-slate-300 leading-normal flex items-start space-x-2">
                          <span className="text-teal-500 font-bold shrink-0">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {recTab === 'marketing' && (
                  <div className="space-y-4">
                    <h3 className="text-sm font-bold text-teal-450 border-b border-slate-900 pb-2">Marketing Recommendations</h3>
                    <ul className="space-y-3">
                      {recommendations.marketing_recommendations && recommendations.marketing_recommendations.map((item, idx) => (
                        <li key={idx} className="text-xs text-slate-300 leading-normal flex items-start space-x-2">
                          <span className="text-teal-500 font-bold shrink-0">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {recTab === 'product' && (
                  <div className="space-y-4">
                    <h3 className="text-sm font-bold text-teal-450 border-b border-slate-900 pb-2">Product Recommendations</h3>
                    <ul className="space-y-3">
                      {recommendations.product_recommendations && recommendations.product_recommendations.map((item, idx) => (
                        <li key={idx} className="text-xs text-slate-300 leading-normal flex items-start space-x-2">
                          <span className="text-teal-500 font-bold shrink-0">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {recTab === 'competitive' && (
                  <div className="space-y-4">
                    <h3 className="text-sm font-bold text-rose-455 border-b border-slate-900 pb-2">Competitive Response Matrix</h3>
                    <div className="space-y-4">
                      {recommendations.competitive_responses && recommendations.competitive_responses.map((resp, idx) => (
                        <div key={idx} className="bg-slate-950/60 border border-slate-900 p-4 rounded-xl space-y-2">
                          <div className="text-xs font-bold text-rose-400">Threat Indicator:</div>
                          <p className="text-xs text-slate-300 font-semibold">{resp.threat}</p>
                          <div className="text-xs font-bold text-teal-400 border-t border-slate-900 pt-2 mt-2">Recommended Response:</div>
                          <p className="text-xs text-slate-400 leading-relaxed">{resp.response}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
