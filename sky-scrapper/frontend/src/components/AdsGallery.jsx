import { Sparkles, Compass, EyeOff, Megaphone, Smartphone, HelpCircle, Layers } from 'lucide-react';

export default function AdsGallery({ adsAnalysis, rawCompetitors }) {
  if (!adsAnalysis) return null;

  const { dominant_messaging_themes, competitor_ad_strategies, content_gaps, recommended_angles } = adsAnalysis;

  // Flatten all raw ads to show a gallery of active ads
  const allAds = [];
  if (rawCompetitors) {
    rawCompetitors.forEach(comp => {
      if (comp.ads && Array.isArray(comp.ads)) {
        comp.ads.forEach(ad => {
          allAds.push({
            ...ad,
            companyName: comp.name
          });
        });
      }
    });
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-100">Advertising & Messaging Intelligence</h2>
        <p className="text-slate-400 text-xs mt-1">
          Analysis of competitors' active digital ad placements, strategic messaging, and market messaging recommendations.
        </p>
      </div>

      {/* Themes and Strategy Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left column: Messaging Summary (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Dominant Themes */}
          <div className="glass-card p-5 space-y-4">
            <h3 className="text-sm font-bold text-teal-400 flex items-center space-x-2 border-b border-slate-900 pb-2">
              <Megaphone className="w-4 h-4" />
              <span>Dominant Messaging Themes</span>
            </h3>
            <div className="flex flex-wrap gap-2">
              {dominant_messaging_themes && dominant_messaging_themes.length > 0 ? (
                dominant_messaging_themes.map((theme, idx) => (
                  <span 
                    key={idx}
                    className="px-3 py-1 rounded-xl bg-teal-500/10 text-teal-300 border border-teal-500/20 text-xs font-medium"
                  >
                    {theme}
                  </span>
                ))
              ) : (
                <span className="text-slate-500 text-xs italic">No themes resolved</span>
              )}
            </div>
          </div>

          {/* Gaps & Angles */}
          <div className="glass-card p-5 space-y-5">
            {/* Content Gaps */}
            <div className="space-y-2">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest flex items-center space-x-1">
                <EyeOff className="w-3.5 h-3.5 text-rose-400" />
                <span>Uncovered Gaps</span>
              </span>
              <ul className="space-y-1.5 pl-0">
                {content_gaps && content_gaps.length > 0 ? (
                  content_gaps.map((gap, idx) => (
                    <li key={idx} className="text-xs text-slate-300 leading-relaxed flex items-start space-x-1.5">
                      <span className="text-slate-500">•</span>
                      <span>{gap}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-slate-500 text-xs italic">No gaps determined</li>
                )}
              </ul>
            </div>

            {/* Recommended Angles */}
            <div className="space-y-2 border-t border-slate-900/60 pt-4">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest flex items-center space-x-1">
                <Sparkles className="w-3.5 h-3.5 text-yellow-400" />
                <span>Recommended Angles</span>
              </span>
              <ul className="space-y-1.5 pl-0">
                {recommended_angles && recommended_angles.length > 0 ? (
                  recommended_angles.map((angle, idx) => (
                    <li key={idx} className="text-xs text-slate-300 leading-relaxed flex items-start space-x-1.5">
                      <span className="text-teal-500">•</span>
                      <span>{angle}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-slate-500 text-xs italic">No recommendations</li>
                )}
              </ul>
            </div>
          </div>
        </div>

        {/* Right column: Competitor Strategies (7 cols) */}
        <div className="lg:col-span-7 glass-card p-5 space-y-4">
          <h3 className="text-sm font-bold text-blue-400 flex items-center space-x-2 border-b border-slate-900 pb-2">
            <Layers className="w-4 h-4" />
            <span>Competitor Ad Strategies</span>
          </h3>
          
          <div className="space-y-4 max-h-[360px] overflow-y-auto pr-1">
            {competitor_ad_strategies && competitor_ad_strategies.length > 0 ? (
              competitor_ad_strategies.map((strat, idx) => (
                <div key={idx} className="bg-slate-950/60 border border-slate-900 p-4 rounded-xl space-y-2">
                  <div className="flex justify-between items-center">
                    <strong className="text-sm text-slate-200">{strat.company}</strong>
                    <span className="text-[10px] font-semibold bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded border border-blue-500/20 uppercase tracking-wider">
                      CTA: {strat.top_cta || 'Learn More'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{strat.strategy}</p>
                </div>
              ))
            ) : (
              <div className="text-slate-600 italic text-xs text-center py-20">
                No active competitor strategies mapped.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Ads Live Gallery Feed */}
      {allAds.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-300 flex items-center space-x-2 pl-1">
            <Smartphone className="w-4.5 h-4.5 text-teal-400" />
            <span>Active Promotion Placements</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {allAds.slice(0, 9).map((ad, idx) => (
              <div key={idx} className="glass-card hover:border-slate-700/80 p-5 flex flex-col justify-between h-[280px]">
                <div className="space-y-3">
                  <div className="flex justify-between items-center text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                    <span>{ad.companyName}</span>
                    <span>{ad.date_seen || 'Recent'}</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed line-clamp-6 bg-slate-950/40 border border-slate-900 p-2.5 rounded-lg font-mono">
                    "{ad.text}"
                  </p>
                </div>

                <div className="border-t border-slate-900/60 pt-3 mt-4 flex items-center justify-between">
                  <div className="flex space-x-1.5">
                    {ad.platforms && ad.platforms.map((p) => (
                      <span 
                        key={p} 
                        className="px-1.5 py-0.5 rounded bg-slate-950 text-[9px] font-medium text-slate-400 border border-slate-800"
                      >
                        {p}
                      </span>
                    ))}
                  </div>
                  <span className="text-[10px] font-bold text-teal-400 bg-teal-500/10 px-2.5 py-1 rounded border border-teal-500/20 uppercase tracking-wide">
                    {ad.cta || 'Learn More'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
