import { Building2, TrendingUp, Users, DollarSign, MapPin, Milestone } from 'lucide-react';

export default function MetricsGrid({ targetCompany, competitors }) {
  if (!targetCompany) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-100">Financial & Business Metrics</h2>
        <p className="text-slate-400 text-xs mt-1">
          Comparative analysis detailing estimated revenues, employee statistics, funding, and growth benchmarks.
        </p>
      </div>

      {/* Grid Table */}
      <div className="glass-panel overflow-hidden border border-slate-800/80">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="bg-slate-900/80 border-b border-slate-800 text-slate-400 text-[11px] font-semibold uppercase tracking-wider">
                <th className="py-4 px-6">Company</th>
                <th className="py-4 px-6">Est. Revenue</th>
                <th className="py-4 px-6">Employees</th>
                <th className="py-4 px-6">Employee Growth</th>
                <th className="py-4 px-6">Funding Raised</th>
                <th className="py-4 px-6">HQ Location</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-900/60">
              {/* Target Company Row */}
              <tr className="bg-teal-500/5 hover:bg-teal-500/10 transition-colors">
                <td className="py-4 px-6 font-bold text-slate-100 flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-teal-500 animate-pulse-glow" />
                  <span>{targetCompany.name} (Target)</span>
                </td>
                <td className="py-4 px-6 font-semibold text-slate-200">{targetCompany.metrics?.revenue || 'N/A'}</td>
                <td className="py-4 px-6 text-slate-300">{targetCompany.metrics?.employees || 'N/A'}</td>
                <td className="py-4 px-6 text-emerald-400 font-semibold">{targetCompany.metrics?.growth_percentage || 'N/A'}</td>
                <td className="py-4 px-6 text-teal-400 font-semibold">{targetCompany.metrics?.funding || 'N/A'}</td>
                <td className="py-4 px-6 text-slate-400">{targetCompany.metrics?.hq_location || 'N/A'}</td>
              </tr>

              {/* Competitors Rows */}
              {competitors && competitors.length > 0 ? (
                competitors.map((comp, idx) => (
                  <tr key={idx} className="hover:bg-slate-900/35 transition-colors">
                    <td className="py-4 px-6 font-semibold text-slate-300">{comp.name}</td>
                    <td className="py-4 px-6 text-slate-300">{comp.metrics?.revenue || 'N/A'}</td>
                    <td className="py-4 px-6 text-slate-400">{comp.metrics?.employees || 'N/A'}</td>
                    <td className="py-4 px-6 text-slate-400">{comp.metrics?.growth_percentage || 'N/A'}</td>
                    <td className="py-4 px-6 text-slate-400">{comp.metrics?.funding || 'N/A'}</td>
                    <td className="py-4 px-6 text-slate-400">{comp.metrics?.hq_location || 'N/A'}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-slate-500 italic">No competitors data compiled.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* Quick summaries cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
        {/* Rev Metric */}
        <div className="glass-card p-4 flex items-center space-x-3">
          <div className="p-3 bg-teal-500/10 rounded-xl border border-teal-500/20 text-teal-400">
            <DollarSign className="w-5 h-5" />
          </div>
          <div>
            <span className="block text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Target Revenue</span>
            <strong className="block text-sm text-slate-200 mt-0.5">{targetCompany.metrics?.revenue || 'N/A'}</strong>
          </div>
        </div>

        {/* Growth Metric */}
        <div className="glass-card p-4 flex items-center space-x-3">
          <div className="p-3 bg-emerald-500/10 rounded-xl border border-emerald-500/20 text-emerald-400">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <span className="block text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Target Growth</span>
            <strong className="block text-sm text-slate-200 mt-0.5">{targetCompany.metrics?.growth_percentage || 'N/A'}</strong>
          </div>
        </div>

        {/* Employees Metric */}
        <div className="glass-card p-4 flex items-center space-x-3">
          <div className="p-3 bg-blue-500/10 rounded-xl border border-blue-500/20 text-blue-400">
            <Users className="w-5 h-5" />
          </div>
          <div>
            <span className="block text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Target Employees</span>
            <strong className="block text-sm text-slate-200 mt-0.5">{targetCompany.metrics?.employees || 'N/A'}</strong>
          </div>
        </div>

        {/* Location Metric */}
        <div className="glass-card p-4 flex items-center space-x-3">
          <div className="p-3 bg-purple-500/10 rounded-xl border border-purple-500/20 text-purple-400">
            <MapPin className="w-5 h-5" />
          </div>
          <div>
            <span className="block text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Headquarters</span>
            <strong className="block text-sm text-slate-200 mt-0.5">{targetCompany.metrics?.hq_location || 'N/A'}</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
