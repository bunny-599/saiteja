import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Smile, Frown, Sparkles, AlertOctagon, Heart } from 'lucide-react';

export default function SentimentChart({ sentiment }) {
  if (!sentiment) return null;

  const { overall_score, sentiment_breakdown, top_praise_themes, top_complaint_themes, urgent_issues, nps_estimate } = sentiment;
  
  // Format data for Recharts Pie
  const data = [
    { name: 'Positive', value: sentiment_breakdown?.positive || 0, color: '#14b8a6' }, // Teal
    { name: 'Neutral', value: sentiment_breakdown?.neutral || 0, color: '#64748b' },  // Slate
    { name: 'Negative', value: sentiment_breakdown?.negative || 0, color: '#f43f5e' }  // Rose
  ].filter(item => item.value > 0);

  const getNpsBadgeColor = (nps) => {
    if (nps > 30) return 'text-teal-400 bg-teal-500/10 border-teal-500/20';
    if (nps > 0) return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
    return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-100">Customer Sentiment Analysis</h2>
        <p className="text-slate-400 text-xs mt-1">
          Synthesized review analysis highlighting customer feedback themes and Net Promoter Score (NPS) projections.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* Donut Chart (5 cols) */}
        <div className="lg:col-span-5 flex flex-col items-center justify-center bg-slate-950/40 border border-slate-900 rounded-2xl p-6 relative">
          <div className="w-full h-56 relative flex items-center justify-center">
            {data.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data}
                    cx="50%"
                    cy="50%"
                    innerRadius={65}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {data.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#090d16', border: '1px solid #1e293b', borderRadius: '8px' }}
                    itemStyle={{ color: '#cbd5e1', fontSize: '12px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-slate-600 text-xs">No chart data available</div>
            )}
            
            {/* Center Text inside Donut */}
            <div className="absolute text-center">
              <span className="block text-3xl font-extrabold text-white tracking-tight">
                {overall_score ? overall_score.toFixed(1) : '0.0'}
              </span>
              <span className="block text-[10px] text-slate-500 font-semibold uppercase tracking-widest mt-0.5">
                Rating / 10
              </span>
            </div>
          </div>

          {/* Legend and NPS */}
          <div className="flex items-center justify-between w-full border-t border-slate-900 pt-4 mt-2">
            <div className="flex space-x-4 text-xs font-semibold">
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-teal-500" />
                <span className="text-slate-400">Pos ({sentiment_breakdown?.positive || 0}%)</span>
              </span>
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-slate-500" />
                <span className="text-slate-400">Neu ({sentiment_breakdown?.neutral || 0}%)</span>
              </span>
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                <span className="text-slate-400">Neg ({sentiment_breakdown?.negative || 0}%)</span>
              </span>
            </div>

            <div className={`flex flex-col items-center px-3 py-1 border rounded-lg ${getNpsBadgeColor(nps_estimate)}`}>
              <span className="text-sm font-bold leading-tight">{nps_estimate || 0}</span>
              <span className="text-[8px] font-semibold uppercase tracking-wider text-slate-500">Est. NPS</span>
            </div>
          </div>
        </div>

        {/* Themes Grid (7 cols) */}
        <div className="lg:col-span-7 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Praise Themes */}
          <div className="glass-card p-5 space-y-4">
            <h3 className="text-sm font-bold text-teal-400 flex items-center space-x-2 border-b border-slate-900 pb-2">
              <Smile className="w-4 h-4" />
              <span>Customer Praise Themes</span>
            </h3>
            <ul className="space-y-2">
              {top_praise_themes && top_praise_themes.length > 0 ? (
                top_praise_themes.map((theme, idx) => (
                  <li key={idx} className="flex items-start space-x-2 text-xs text-slate-300 leading-normal">
                    <span className="text-teal-500 shrink-0">•</span>
                    <span>{theme}</span>
                  </li>
                ))
              ) : (
                <li className="text-slate-500 italic text-xs">No praise themes logged.</li>
              )}
            </ul>
          </div>

          {/* Complaint Themes */}
          <div className="glass-card p-5 space-y-4">
            <h3 className="text-sm font-bold text-rose-400 flex items-center space-x-2 border-b border-slate-900 pb-2">
              <Frown className="w-4 h-4" />
              <span>Customer Complaint Themes</span>
            </h3>
            <ul className="space-y-2">
              {top_complaint_themes && top_complaint_themes.length > 0 ? (
                top_complaint_themes.map((theme, idx) => (
                  <li key={idx} className="flex items-start space-x-2 text-xs text-slate-300 leading-normal">
                    <span className="text-rose-500 shrink-0">•</span>
                    <span>{theme}</span>
                  </li>
                ))
              ) : (
                <li className="text-slate-500 italic text-xs">No complaint themes logged.</li>
              )}
            </ul>
          </div>
        </div>
      </div>

      {/* Urgent Issues Warning Banner */}
      {urgent_issues && urgent_issues.length > 0 && (
        <div className="bg-rose-500/5 border border-rose-500/20 rounded-2xl p-5 space-y-3">
          <h3 className="text-xs font-bold text-rose-400 uppercase tracking-widest flex items-center space-x-2">
            <AlertOctagon className="w-4.5 h-4.5" />
            <span>Urgent Customer Experience Issues (Action Required)</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {urgent_issues.map((issue, idx) => (
              <div key={idx} className="flex items-start space-x-2 bg-slate-950/40 p-3 rounded-xl border border-rose-950/20 text-xs text-slate-300">
                <span className="text-rose-500 shrink-0 font-bold">•</span>
                <span>{issue}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
