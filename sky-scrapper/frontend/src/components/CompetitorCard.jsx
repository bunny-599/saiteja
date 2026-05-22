import { Globe, ShieldAlert, Award, AlertCircle, Coins, CheckCircle, ExternalLink, Star } from 'lucide-react';

export default function CompetitorCard({ profile, rawData }) {
  if (!profile) return null;

  const { company, positioning, target_audience, key_strengths, key_weaknesses, pricing_model, estimated_market_share_tier } = profile;
  
  // Get ratings and tech stack from rawData if available
  const rating = rawData?.average_rating || 0;
  const reviewCount = rawData?.review_count || 0;
  const techStack = rawData?.detected_tech_stack || [];
  const tagline = rawData?.tagline || '';
  const domain = rawData?.domain || '';

  const getTierColor = (tier) => {
    switch (tier?.toLowerCase()) {
      case 'leader':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'challenger':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'niche':
        return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
    }
  };

  return (
    <div className="glass-panel hover:border-slate-700/80 transition-all p-6 space-y-6 flex flex-col justify-between">
      <div className="space-y-4">
        {/* Header Name & Tier */}
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
              <span>{company}</span>
              {domain && (
                <a 
                  href={`https://${domain}`} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-slate-500 hover:text-teal-400 transition-colors"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </h3>
            {tagline && <p className="text-xs text-slate-400 mt-1 italic">"{tagline}"</p>}
          </div>
          
          <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider border ${getTierColor(estimated_market_share_tier)}`}>
            {estimated_market_share_tier || 'Niche'}
          </span>
        </div>

        {/* Rating Score */}
        {reviewCount > 0 && (
          <div className="flex items-center space-x-2 text-sm text-slate-300 bg-slate-950/40 w-fit px-3 py-1 rounded-lg border border-slate-900">
            <Star className="w-4 h-4 fill-amber-400 stroke-amber-400" />
            <span><strong>{rating.toFixed(1)}</strong> rating</span>
            <span className="text-slate-500">({reviewCount} reviews)</span>
          </div>
        )}

        {/* Positioning */}
        <div className="space-y-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Market Positioning</span>
          <p className="text-sm text-slate-300 leading-relaxed">{positioning}</p>
        </div>

        {/* Target Audience */}
        <div className="space-y-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Target Audience</span>
          <p className="text-sm text-slate-300 leading-relaxed">{target_audience}</p>
        </div>

        {/* Strengths & Weaknesses Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {/* Strengths */}
          <div className="space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-emerald-500 flex items-center space-x-1">
              <CheckCircle className="w-3.5 h-3.5" />
              <span>Strengths</span>
            </span>
            <ul className="text-xs text-slate-300 space-y-1.5 list-none pl-0">
              {key_strengths && key_strengths.length > 0 ? (
                key_strengths.map((str, idx) => (
                  <li key={idx} className="flex items-start space-x-1.5">
                    <span className="text-emerald-500">•</span>
                    <span>{str}</span>
                  </li>
                ))
              ) : (
                <li className="text-slate-500 italic">No details compiled</li>
              )}
            </ul>
          </div>

          {/* Weaknesses */}
          <div className="space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-orange-500 flex items-center space-x-1">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>Weaknesses</span>
            </span>
            <ul className="text-xs text-slate-300 space-y-1.5 list-none pl-0">
              {key_weaknesses && key_weaknesses.length > 0 ? (
                key_weaknesses.map((weak, idx) => (
                  <li key={idx} className="flex items-start space-x-1.5">
                    <span className="text-orange-500">•</span>
                    <span>{weak}</span>
                  </li>
                ))
              ) : (
                <li className="text-slate-500 italic">No details compiled</li>
              )}
            </ul>
          </div>
        </div>
      </div>

      <div className="border-t border-slate-900/60 pt-4 mt-6 space-y-4">
        {/* Pricing */}
        <div className="flex items-center space-x-2 text-xs text-slate-400 bg-slate-950/40 p-2.5 rounded-xl border border-slate-900">
          <Coins className="w-4 h-4 text-teal-400 shrink-0" />
          <div>
            <span className="font-semibold text-slate-300">Pricing Model:</span>{' '}
            <span>{pricing_model || 'Data not available'}</span>
          </div>
        </div>

        {/* Tech Stack clues */}
        {techStack.length > 0 && (
          <div className="space-y-1.5">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">Tech Stack Indicators</span>
            <div className="flex flex-wrap gap-1">
              {techStack.map((tech) => (
                <span 
                  key={tech} 
                  className="px-2 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800 text-[10px] font-medium"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
