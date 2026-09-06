import React, { useState, useEffect } from 'react';

type Theme = {
  id: string;
  name: string;
  description: string;
  count: number;
  percentage: string;
  priority: string;
};

export const Pulse: React.FC = () => {
  const [themes, setThemes] = useState<Theme[]>([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/dashboard/themes')
      .then(res => res.json())
      .then(data => setThemes(data))
      .catch(console.error);
  }, []);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'CRITICAL': return 'bg-error-light dark:bg-error/20 text-error';
      case 'HIGH': return 'bg-warning/20 text-warning';
      default: return 'bg-primary/20 text-primary';
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center justify-center w-2 h-2 rounded-full bg-primary animate-pulse"></span>
          <span className="text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 font-bold">Themes & Pulse</span>
        </div>
      </div>
      
      <div className="bg-white dark:bg-card-dark rounded-2xl p-5 border border-slate-200/80 dark:border-border-dark shadow-sm">
        <h2 className="font-heading text-lg font-bold text-slate-900 dark:text-white mb-4">Top User Themes List</h2>
        <div className="flex flex-col gap-4">
          {themes.map(theme => (
            <div key={theme.id} className="flex items-center justify-between p-4 bg-slate-50 dark:bg-card-dark-subtle rounded-xl border border-slate-100 dark:border-border-dark-light">
              <div>
                <h3 className="font-semibold text-slate-800 dark:text-slate-100 text-sm">{theme.name}</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{theme.description}</p>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="text-xs font-medium text-slate-900 dark:text-white">{theme.count} Reviews</div>
                  <div className="text-[10px] text-slate-500">{theme.percentage} of total</div>
                </div>
                <span className={`px-2 py-1 rounded-md text-[10px] font-bold ${getPriorityColor(theme.priority)}`}>
                  {theme.priority}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
