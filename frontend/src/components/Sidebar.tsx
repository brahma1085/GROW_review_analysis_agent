import React from 'react';
import { NavLink } from 'react-router-dom';
import clsx from 'clsx';

export const Sidebar: React.FC = () => {
  const navLinkClasses = ({ isActive }: { isActive: boolean }) =>
    clsx(
      'flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold transition-all',
      isActive
        ? 'bg-primary/10 text-primary'
        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100/70 dark:hover:bg-slate-800/60'
    );

  return (
    <aside className="hidden lg:flex flex-col w-64 flex-shrink-0 bg-white dark:bg-[#0d1424] border-r border-slate-200 dark:border-[#1e293b] sticky top-0 h-screen z-40 transition-colors duration-200 justify-between">
      <div>
        <div className="h-16 flex items-center px-6 border-b border-slate-100 dark:border-[#1e293b]/70">
          <div className="flex items-center gap-2.5">
            <img
              alt="Groww Intel Logo"
              className="h-8 w-auto object-contain dark:brightness-110"
              src="https://lh3.googleusercontent.com/aida/AEtjO1VZsgXVeWlfXB67KP2TYn5CAdTqx9Z6txI_7LgA3wmtNftd4Kuinw9dq4T76kUfaGvwZzYfBpmK-bALF8mRvkspRn0A8L9-V8FaInXtmMmkQg-API8_KrsVTOnbp-F54nE9VB0eZFzy8Xoe8Lw8QhK0f1ZjkHrKBgfN152RjfPARdeMpzS84LLBQc47hLe0Er29ziIgb0CoBsrDj1FG1hOzY_ak0ctq4UdciWoiogHcJ2IQ-KdVNX9Bqk2H"
            />
          </div>
        </div>

        <nav className="p-4 space-y-1.5 font-medium text-sm">
          <div className="px-3 pb-2 text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
            Analytics & Pulse
          </div>
          <NavLink to="/" className={navLinkClasses}>
            <span className="material-symbols-outlined text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>
              insights
            </span>
            <span>Dashboard</span>
          </NavLink>
          <NavLink to="/trends" className={navLinkClasses}>
            <span className="material-symbols-outlined text-[20px]">trending_up</span>
            <span>Trends & Themes</span>
          </NavLink>
          <NavLink to="/product-areas" className={navLinkClasses}>
            <span className="material-symbols-outlined text-[20px]">category</span>
            <span>Product Areas</span>
          </NavLink>
          <NavLink to="/voc" className={navLinkClasses}>
            <span className="material-symbols-outlined text-[20px]">mark_chat_read</span>
            <span>VoC Explorer</span>
          </NavLink>

          <div className="pt-4 px-3 pb-2 text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
            System & Settings
          </div>
          <NavLink to="/admin" className={navLinkClasses}>
            <span className="material-symbols-outlined text-[20px]">tune</span>
            <span>Admin Controls</span>
          </NavLink>
          <NavLink to="/logs" className={navLinkClasses}>
            <span className="material-symbols-outlined text-[20px]">history</span>
            <span>Logs & History</span>
          </NavLink>
        </nav>
      </div>

      <div className="p-4 m-3 rounded-xl bg-slate-50 dark:bg-[#131b2e] border border-slate-200/80 dark:border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">NLP Engine v4.2</span>
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-primary">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-ping"></span> Operational
          </span>
        </div>
        <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
          Processing 14.8k signals/week with 99.8% precision rate.
        </p>
      </div>
    </aside>
  );
};
