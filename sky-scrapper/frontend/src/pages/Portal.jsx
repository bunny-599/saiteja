import { Link } from 'react-router-dom';
import { ShieldAlert, Megaphone, Lightbulb, ArrowRight } from 'lucide-react';

export default function Portal() {
  const tools = [
    {
      title: 'Competitor SWOT Analyzer',
      desc: 'Run specialized competitor profiling and corporate SWOT matrices. Scrapes taglines, product positioning, value propositions, and tech stacks.',
      icon: <ShieldAlert className="w-8 h-8 text-teal-400" />,
      path: '/analyze',
      badge: 'Competitor & SWOT',
      glowClass: 'hover:shadow-[0_0_30px_rgba(20,184,166,0.15)] hover:border-teal-500/50',
      badgeColor: 'bg-teal-500/10 text-teal-400 border-teal-500/20',
      arrowColor: 'text-teal-400'
    },
    {
      title: 'Marketing & Ads Intelligence',
      desc: 'Analyze client sentiment, Trustpilot feedback, and active social media advertising patterns. Indexes and evaluates live Meta Ad Library campaigns.',
      icon: <Megaphone className="w-8 h-8 text-blue-400" />,
      path: '/marketing',
      badge: 'Sentiment & Ads',
      glowClass: 'hover:shadow-[0_0_30px_rgba(59,130,246,0.15)] hover:border-blue-500/50',
      badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      arrowColor: 'text-blue-400'
    },
    {
      title: 'Future Gaps & Strategy',
      desc: 'Map market opportunities, financial growth vectors, and news alerts. Recommends a weekly and monthly operational strategic response roadmap.',
      icon: <Lightbulb className="w-8 h-8 text-amber-400" />,
      path: '/future',
      badge: 'Opportunities & Strategy',
      glowClass: 'hover:shadow-[0_0_30px_rgba(245,158,11,0.15)] hover:border-amber-500/50',
      badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      arrowColor: 'text-amber-400'
    }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24 space-y-12">
      {/* Hero Header */}
      <div className="text-center max-w-3xl mx-auto space-y-4">
        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-teal-500/10 text-teal-400 border border-teal-500/20 uppercase tracking-wider">
          Intelligence Suite
        </span>
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white leading-none">
          Sky-Scrapper AI{' '}
          <span className="bg-gradient-to-r from-teal-400 via-blue-500 to-amber-400 bg-clip-text text-transparent">
            Intelligence
          </span>
        </h1>
        <p className="text-slate-400 text-base md:text-lg leading-relaxed">
          Select a specialized intelligence engine. Each module coordinates target web scraping routines and utilizes tailored Claude AI prompts to compile tactical reports.
        </p>
      </div>

      {/* Grid selector */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-6">
        {tools.map((tool, idx) => (
          <Link 
            key={idx} 
            to={tool.path}
            className={`group glass-panel p-8 flex flex-col justify-between hover:-translate-y-1.5 transition-all duration-300 border border-slate-800 bg-slate-900/20 cursor-pointer ${tool.glowClass}`}
          >
            <div className="space-y-6">
              {/* Header block */}
              <div className="flex items-center justify-between">
                <div className="p-3 bg-slate-950 rounded-xl border border-slate-850">
                  {tool.icon}
                </div>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold border uppercase tracking-wider ${tool.badgeColor}`}>
                  {tool.badge}
                </span>
              </div>

              {/* Body */}
              <div className="space-y-2">
                <h3 className="text-xl font-bold text-slate-100 group-hover:text-white transition-colors">
                  {tool.title}
                </h3>
                <p className="text-slate-400 text-sm leading-relaxed">
                  {tool.desc}
                </p>
              </div>
            </div>

            {/* CTA Arrow */}
            <div className="flex items-center space-x-2 text-xs font-bold pt-8 mt-auto group-hover:underline">
              <span className="text-slate-350 group-hover:text-white transition-colors">Launch Module</span>
              <ArrowRight className={`w-4 h-4 transition-transform group-hover:translate-x-1 ${tool.arrowColor}`} />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
