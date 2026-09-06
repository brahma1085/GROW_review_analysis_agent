import React from 'react';
import { useTheme } from '../theme/ThemeProvider';

export const Header: React.FC = () => {
  const { theme, setTheme } = useTheme();

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <header className="sticky top-0 z-30 bg-white/90 dark:bg-[#090d16]/90 backdrop-blur-md border-b border-slate-200/80 dark:border-[#1e293b] transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 lg:hidden">
          <img
            alt="Groww Intel Logo"
            className="h-7 w-auto object-contain dark:brightness-110"
            src="https://lh3.googleusercontent.com/aida/AEtjO1VZsgXVeWlfXB67KP2TYn5CAdTqx9Z6txI_7LgA3wmtNftd4Kuinw9dq4T76kUfaGvwZzYfBpmK-bALF8mRvkspRn0A8L9-V8FaInXtmMmkQg-API8_KrsVTOnbp-F54nE9VB0eZFzy8Xoe8Lw8QhK0f1ZjkHrKBgfN152RjfPARdeMpzS84LLBQc47hLe0Er29ziIgb0CoBsrDj1FG1hOzY_ak0ctq4UdciWoiogHcJ2IQ-KdVNX9Bqk2H"
          />
        </div>
        <div className="hidden md:flex items-center flex-1 max-w-md relative">
          <span className="material-symbols-outlined absolute left-3 text-slate-400 text-[18px]">search</span>
          <input
            className="w-full pl-9 pr-4 py-2 text-xs rounded-xl bg-slate-100 dark:bg-[#131b2e] border border-slate-200/80 dark:border-slate-700/60 focus:outline-none focus:ring-2 focus:ring-primary/50 text-slate-800 dark:text-slate-200 placeholder-slate-400 transition-colors"
            placeholder="Search feedback, issues, keywords (e.g. 'UPI pause', 'KYC timeout')..."
            type="text"
          />
          <kbd className="absolute right-2.5 px-1.5 py-0.5 text-[10px] font-semibold text-slate-400 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded shadow-xs">
            ⌘K
          </kbd>
        </div>
        <div className="flex items-center gap-2.5 sm:gap-3 ml-auto">
          <button className="h-9 px-3 rounded-xl bg-slate-100 dark:bg-[#131b2e] border border-slate-200/80 dark:border-slate-700/60 hover:bg-slate-200/60 dark:hover:bg-slate-800/80 flex items-center gap-1.5 text-slate-700 dark:text-slate-300 text-xs font-semibold transition-all">
            <span className="material-symbols-outlined text-[16px] text-primary">calendar_today</span>
            <span>Week 42, 2024</span>
            <span className="material-symbols-outlined text-[16px] text-slate-400">expand_more</span>
          </button>
          <button
            onClick={toggleTheme}
            aria-label="Toggle Light and Dark Mode"
            className="h-9 px-2.5 sm:px-3 rounded-xl bg-slate-100 dark:bg-[#131b2e] border border-slate-200/80 dark:border-slate-700/60 hover:bg-slate-200/60 dark:hover:bg-slate-800/80 flex items-center gap-1.5 text-slate-700 dark:text-slate-300 text-xs font-medium transition-all group"
          >
            {theme === 'dark' ? (
              <span className="material-symbols-outlined text-[18px] text-amber-500">light_mode</span>
            ) : (
              <span className="material-symbols-outlined text-[18px] text-slate-600">dark_mode</span>
            )}
            <span className="hidden sm:inline text-xs font-medium">
              {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
            </span>
          </button>
          <button
            aria-label="Notifications"
            className="relative w-9 h-9 rounded-xl flex items-center justify-center text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-[#131b2e] border border-slate-200/80 dark:border-slate-700/60 hover:bg-slate-200/60 dark:hover:bg-slate-800/80 transition-all"
          >
            <span className="material-symbols-outlined text-[18px]">notifications</span>
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-error ring-2 ring-white dark:ring-[#090d16]"></span>
          </button>
          <div className="flex items-center gap-2 pl-1 sm:pl-2 border-l border-slate-200 dark:border-slate-800">
            <img
              alt="Executive Profile"
              className="w-8 h-8 rounded-xl object-cover ring-2 ring-primary/40 shadow-xs"
              src="https://lh3.googleusercontent.com/aida/AEtjO1WOIZ7FtDM3RkH_4q4hDtrl9TI22iTc1685AHm3P-jgaiByEHW8w3HuKOahbrdjSMF53TE5SFa9VG6j41GQzk2Qvk2pHjPSOPeaUgmxPEXLhQW1Y2EDVs9UseoSc2onGCZ_iB5SCyT66Nqpcyi94xXomuy5DlVd-5Bh7PNgzdnAuQWov0Y0Vf6aL9e89AIjWWQNTvP6mfs7sS5dXR8D6B45QLxxjM1seVblNI1YjBIRgLHMv20wi12VLQK5"
            />
            <div className="hidden xl:block text-left">
              <div className="text-xs font-semibold text-slate-900 dark:text-white leading-tight">Sarah Jenkins</div>
              <div className="text-[11px] text-slate-400">Head of Product</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
