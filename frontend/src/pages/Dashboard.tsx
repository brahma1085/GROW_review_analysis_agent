import React, { useEffect, useState } from 'react';

type DashboardSummary = {
  health_score: number;
  health_score_delta: string;
  avg_star_rating: number;
  positive_sentiment: string;
  total_reviews: string;
  negative_reviews: number;
  sentiment_breakdown: {
    positive: number;
    neutral: number;
    negative: number;
  };
};

type Theme = {
  id: string;
  name: string;
  description: string;
  count: number;
  percentage: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
};

export const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [themes, setThemes] = useState<Theme[]>([]);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/dashboard/summary`)
      .then(res => res.json())
      .then(data => setSummary(data))
      .catch(console.error);
      
    fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/dashboard/themes`)
      .then(res => res.json())
      .then(data => setThemes(data))
      .catch(console.error);
  }, []);

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center justify-center w-2 h-2 rounded-full bg-primary animate-pulse"></span>
          <span className="text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 font-bold">Executive Cockpit</span>
          <span className="hidden sm:inline text-slate-300 dark:text-slate-700">|</span>
          <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">Weekly Insights & Operational Health</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] bg-slate-100 dark:bg-[#131b2e] text-slate-600 dark:text-slate-400 border border-slate-200/80 dark:border-slate-800 px-2.5 py-1 rounded-full font-medium flex items-center gap-1.5">
            <span className="material-symbols-outlined text-[14px] text-primary">sync</span> Real-time Sync (12m ago)
          </span>
          <button className="text-xs text-primary font-semibold hover:underline hidden sm:inline-flex items-center gap-0.5">
            Refresh Data
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4 sm:gap-6 mt-6">
        <section className="md:col-span-12 lg:col-span-6 xl:col-span-6 bg-white dark:bg-[#131b2e] rounded-2xl border border-slate-200/90 dark:border-slate-800/80 p-5 sm:p-6 shadow-xs transition-colors duration-200 flex flex-col justify-between">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Overall App Health Score</span>
              <div className="flex flex-wrap items-baseline gap-2 mt-1">
                <span className="font-heading text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                  {summary ? summary.health_score : '-'}
                </span>
                <span className="text-base text-slate-400 dark:text-slate-500 font-medium">/ 10</span>
                <span className="inline-flex items-center gap-0.5 ml-1 px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-semibold">
                  <span className="material-symbols-outlined text-[14px]">arrow_upward</span> {summary?.health_score_delta}
                </span>
              </div>
            </div>
            <div className="relative w-14 h-14 sm:w-16 sm:h-16 flex-shrink-0">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                <path className="text-slate-100 dark:text-slate-800" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3.2"></path>
                <path className="text-primary" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray="84, 100" strokeLinecap="round" strokeWidth="3.2"></path>
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="material-symbols-outlined text-[22px] text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>verified</span>
              </div>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800/80 flex items-center gap-3">
            <div className="flex-1">
              <div className="text-[10px] text-slate-400 font-medium uppercase tracking-wider mb-1">Avg Star Rating</div>
              <div className="flex items-center gap-1 text-slate-900 dark:text-white font-bold text-sm">
                {summary ? summary.avg_star_rating : '-'} <span className="material-symbols-outlined text-[14px] text-amber-500" style={{ fontVariationSettings: "'FILL' 1" }}>star</span>
              </div>
            </div>
            <div className="w-px h-8 bg-slate-200 dark:bg-slate-700/60"></div>
            <div className="flex-1">
              <div className="text-[10px] text-slate-400 font-medium uppercase tracking-wider mb-1">Positive Sentiment</div>
              <div className="flex items-center gap-1 text-slate-900 dark:text-white font-bold text-sm">
                {summary ? summary.positive_sentiment : '-'} <span className="text-emerald-500 text-xs">↑</span>
              </div>
            </div>
          </div>
        </section>

        <section className="md:col-span-12 lg:col-span-6 xl:col-span-6 bg-white dark:bg-[#131b2e] rounded-2xl border border-slate-200/90 dark:border-slate-800/80 p-5 sm:p-6 shadow-xs transition-colors duration-200 flex flex-col justify-between">
          <div className="flex items-start justify-between mb-4">
            <div>
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Review Volume</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="font-heading text-2xl font-bold text-slate-900 dark:text-white">
                  {summary ? summary.total_reviews : '-'} Total
                </span>
                <span className="text-xs font-semibold text-red-600 dark:text-red-400">
                  {summary ? summary.negative_reviews : '-'} Negative
                </span>
              </div>
            </div>
          </div>
          
          <div>
            <div className="text-[10px] text-slate-400 font-medium uppercase tracking-wider mb-2">Sentiment Breakdown</div>
            <div className="flex h-3 w-full rounded-full overflow-hidden bg-slate-100 dark:bg-slate-800">
              <div style={{ width: `${summary?.sentiment_breakdown?.positive || 0}%` }} className="bg-emerald-500"></div>
              <div style={{ width: `${summary?.sentiment_breakdown?.neutral || 0}%` }} className="bg-amber-400"></div>
              <div style={{ width: `${summary?.sentiment_breakdown?.negative || 0}%` }} className="bg-red-500"></div>
            </div>
            <div className="flex justify-between items-center mt-2 text-xs font-medium">
              <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-400">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span> Positive ({summary?.sentiment_breakdown?.positive || 0}%)
              </div>
              <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-400">
                <span className="w-2 h-2 rounded-full bg-amber-400"></span> Neutral ({summary?.sentiment_breakdown?.neutral || 0}%)
              </div>
              <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-400">
                <span className="w-2 h-2 rounded-full bg-red-500"></span> Negative ({summary?.sentiment_breakdown?.negative || 0}%)
              </div>
            </div>
          </div>
        </section>
        
        {/* Key Themes Section */}
        <section className="md:col-span-12 lg:col-span-12 xl:col-span-12 bg-white dark:bg-[#131b2e] rounded-2xl border border-slate-200/90 dark:border-slate-800/80 p-5 sm:p-6 shadow-xs transition-colors duration-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">Top Detected Themes</h3>
            <span className="text-xs text-slate-500">{themes.length} themes detected</span>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800/80 text-xs text-slate-500 uppercase tracking-wider">
                  <th className="pb-3 font-semibold">Theme & Description</th>
                  <th className="pb-3 font-semibold text-right">Count</th>
                  <th className="pb-3 font-semibold text-right">Impact</th>
                  <th className="pb-3 font-semibold text-center">Priority</th>
                </tr>
              </thead>
              <tbody>
                {themes.slice(0, 5).map((theme) => (
                  <tr key={theme.id} className="border-b border-slate-100 dark:border-slate-800/50 last:border-0 hover:bg-slate-50/50 dark:hover:bg-slate-800/20 transition-colors">
                    <td className="py-4 pr-4">
                      <div className="font-semibold text-sm text-slate-900 dark:text-white mb-1">{theme.name}</div>
                      <div className="text-xs text-slate-500 dark:text-slate-400 max-w-xl truncate">{theme.description}</div>
                    </td>
                    <td className="py-4 px-2 text-right">
                      <span className="font-medium text-sm">{theme.count}</span>
                    </td>
                    <td className="py-4 px-2 text-right">
                      <span className="inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                        {theme.percentage}
                      </span>
                    </td>
                    <td className="py-4 pl-4 text-center">
                      <span className={`inline-flex items-center text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider ${
                        theme.priority === 'CRITICAL' ? 'bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400' :
                        theme.priority === 'HIGH' ? 'bg-amber-100 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400' :
                        'bg-blue-100 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400'
                      }`}>
                        {theme.priority}
                      </span>
                    </td>
                  </tr>
                ))}
                {themes.length === 0 && (
                  <tr>
                    <td colSpan={4} className="py-8 text-center text-sm text-slate-500">No themes detected in the current aggregate.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </>
  );
};
