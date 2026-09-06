import React, { useState, useEffect } from 'react';

export const Admin: React.FC = () => {
  const [statusData, setStatusData] = useState<{status: string, last_run: string, worker_id: string} | null>(null);
  const [isTriggering, setIsTriggering] = useState(false);

  const fetchStatus = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/admin/status');
      const data = await res.json();
      setStatusData(data);
    } catch (e) {
      console.error("Failed to fetch status", e);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  const handleTrigger = async () => {
    setIsTriggering(true);
    try {
      await fetch('http://localhost:8000/api/admin/trigger-run', { method: 'POST' });
      await fetchStatus();
    } catch (e) {
      console.error("Failed to trigger run", e);
    } finally {
      setIsTriggering(false);
    }
  };

  const isRunning = statusData?.status === "Running";

  return (
    <div className="flex-1 px-4 sm:px-6 lg:px-8 py-6 max-w-7xl w-full mx-auto">
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 px-4 py-3 bg-white dark:bg-card-dark rounded-xl border border-slate-200/80 dark:border-border-dark shadow-sm">
        <div className="flex items-center gap-2.5">
          <span className="relative flex h-2.5 w-2.5">
            {isRunning && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>}
            <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${isRunning ? 'bg-primary' : 'bg-slate-400'}`}></span>
          </span>
          <span className="font-heading font-bold text-xs sm:text-sm text-slate-800 dark:text-slate-100">Orchestrator v2.4 Active</span>
          <span className="hidden sm:inline-block w-1 h-1 rounded-full bg-slate-300 dark:bg-slate-600"></span>
          <span className="hidden sm:inline text-xs text-slate-500 dark:text-slate-400">Multi-source NLP aggregation engine</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
          <span className="flex items-center gap-1 text-slate-600 dark:text-slate-300">
            <span className="material-symbols-outlined text-[16px] text-[#006c4f] dark:text-primary">check_circle</span>
            Last run: <span className="font-mono font-medium ml-0.5">{statusData?.last_run || 'Unknown'}</span>
          </span>
          <span className="text-slate-300 dark:text-slate-700">|</span>
          <span className="text-slate-500 dark:text-slate-400 font-mono text-[11px]">Worker ID: {statusData?.worker_id || '#08-HYD'}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div className="lg:col-span-5 flex flex-col gap-6 lg:sticky lg:top-24">
          <div className="bg-white dark:bg-card-dark rounded-2xl p-5 border border-slate-200/80 dark:border-border-dark shadow-sm flex flex-col gap-4">
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-heading text-[11px] uppercase tracking-wider text-[#006c4f] dark:text-primary font-bold">Feedback Intelligence Core</span>
                <span className="bg-primary/15 text-[#006c4f] dark:text-primary px-2 py-0.5 rounded-full text-[11px] font-semibold flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
                  {isRunning ? 'Syncing...' : 'Ready to Sync'}
                </span>
              </div>
              <h2 className="font-heading text-lg sm:text-xl font-bold text-slate-900 dark:text-white">Weekly Synthesis Engine</h2>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
                Triggers automated ingestion across Google Play, App Store, social queries & sentiment vectors.
              </p>
            </div>
            
            <button 
              onClick={handleTrigger}
              disabled={isRunning || isTriggering}
              className={`w-full h-12 ${isRunning || isTriggering ? 'bg-slate-300 dark:bg-slate-700 cursor-not-allowed' : 'bg-primary-dark hover:bg-primary-dark/80 dark:bg-primary dark:hover:bg-primary/80 active:scale-[0.99]'} text-white dark:text-slate-950 font-heading font-semibold rounded-xl shadow-md transition-all flex items-center justify-center gap-2 group`}
            >
              <span className={`material-symbols-outlined text-[20px] ${(!isRunning && !isTriggering) ? 'transition-transform group-hover:rotate-12' : ''}`}>auto_awesome</span>
              <span>{isRunning ? 'Pipeline Running...' : (isTriggering ? 'Triggering...' : 'Trigger AI Agent Run Now')}</span>
              <span className="material-symbols-outlined text-[18px]">bolt</span>
            </button>
            
            <div className="pt-2 border-t border-slate-100 dark:border-slate-800">
              <div className="flex items-center justify-between pb-3">
                <span className="text-xs font-bold text-slate-800 dark:text-slate-200 font-heading">Active Pipeline Status</span>
                <span className="text-xs font-mono font-medium text-primary-dark dark:text-primary">{statusData?.status || 'Unknown'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
