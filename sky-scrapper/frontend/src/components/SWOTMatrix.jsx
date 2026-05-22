import { useState } from 'react';
import { HelpCircle, ChevronRight, CheckCircle2, AlertTriangle, Lightbulb, Skull } from 'lucide-react';

export default function SWOTMatrix({ swot }) {
  const [activeCell, setActiveCell] = useState(null);

  if (!swot) return null;

  const quadrants = [
    {
      key: 'strengths',
      title: 'Strengths',
      icon: <CheckCircle2 className="w-5 h-5 text-emerald-400" />,
      bg: 'bg-emerald-500/5 hover:bg-emerald-500/10 border-emerald-500/20 hover:border-emerald-500/40',
      labelColor: 'text-emerald-400',
      bulletColor: 'text-emerald-500',
      items: swot.strengths || []
    },
    {
      key: 'weaknesses',
      title: 'Weaknesses',
      icon: <AlertTriangle className="w-5 h-5 text-orange-400" />,
      bg: 'bg-orange-500/5 hover:bg-orange-500/10 border-orange-500/20 hover:border-orange-500/40',
      labelColor: 'text-orange-400',
      bulletColor: 'text-orange-500',
      items: swot.weaknesses || []
    },
    {
      key: 'opportunities',
      title: 'Opportunities',
      icon: <Lightbulb className="w-5 h-5 text-blue-400" />,
      bg: 'bg-blue-500/5 hover:bg-blue-500/10 border-blue-500/20 hover:border-blue-500/40',
      labelColor: 'text-blue-400',
      bulletColor: 'text-blue-500',
      items: swot.opportunities || []
    },
    {
      key: 'threats',
      title: 'Threats',
      icon: <Skull className="w-5 h-5 text-red-400" />,
      bg: 'bg-red-500/5 hover:bg-red-500/10 border-red-500/20 hover:border-red-500/40',
      labelColor: 'text-red-400',
      bulletColor: 'text-red-500',
      items: swot.threats || []
    }
  ];

  return (
    <div className="space-y-6">
      {/* Description */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100">SWOT Matrix</h2>
          <p className="text-slate-400 text-xs mt-1">
            Core strengths, internal weaknesses, market opportunities, and critical threats with scraped data references.
          </p>
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {quadrants.map((quad) => (
          <div 
            key={quad.key}
            className={`border rounded-2xl p-6 transition-all duration-300 flex flex-col justify-between h-[360px] overflow-y-auto ${quad.bg}`}
          >
            <div className="space-y-4">
              {/* Header */}
              <div className="flex items-center space-x-2.5 pb-3 border-b border-slate-900/60">
                {quad.icon}
                <span className={`font-bold text-lg tracking-wide ${quad.labelColor}`}>{quad.title}</span>
              </div>
              
              {/* Items List */}
              <div className="space-y-4">
                {quad.items.length > 0 ? (
                  quad.items.map((item, idx) => (
                    <div key={idx} className="space-y-1 group">
                      <div className="flex items-start space-x-2 text-sm text-slate-200">
                        <span className={`shrink-0 font-bold ${quad.bulletColor}`}>•</span>
                        <strong className="font-semibold">{item.point}</strong>
                      </div>
                      
                      {item.evidence && (
                        <div className="pl-4 text-xs text-slate-400 leading-normal flex items-start space-x-1.5 border-l border-slate-800 ml-1 mt-1">
                          <HelpCircle className="w-3.5 h-3.5 text-slate-500 shrink-0 mt-0.5" />
                          <span><em className="text-slate-500">Evidence:</em> {item.evidence}</span>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="text-slate-600 italic text-sm py-16 text-center">
                    No data vectors compiled for {quad.title.toLowerCase()}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
