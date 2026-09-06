import React, { useEffect, useState } from 'react';

type DashboardSummary = {
  health_score: number;
  health_score_delta: string;
  avg_star_rating: number;
  positive_sentiment: string;
  total_reviews: string;
};

export const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/dashboard/summary')
      .then(res => res.json())
      .then(data => setSummary(data))
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
      </div>
    </>
  );
};
