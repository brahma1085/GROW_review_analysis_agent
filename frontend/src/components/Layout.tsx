import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export const Layout: React.FC = () => {
  return (
    <>
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 pb-20 lg:pb-12">
        <Header />
        <main className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 pt-6 space-y-6">
          <Outlet />
        </main>
      </div>
    </>
  );
};
