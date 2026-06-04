import React from 'react';
import {
  DashboardIcon,
  UploadIcon,
  AnalyticsIcon
} from './Icons';

export default function Sidebar({ activeTab, setActiveTab }) {
  // Only keep Dashboard, CSV Uploader, and Analytics as requested
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: DashboardIcon },
    { id: 'uploader', label: 'CSV Uploader', icon: UploadIcon, badge: 'New' },
    { id: 'analytics', label: 'Analytics', icon: AnalyticsIcon },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col h-screen sticky top-0 left-0 border-r border-slate-800 select-none z-30">
      {/* Brand Header */}
      <div className="p-6 border-b border-slate-800 flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-md shadow-blue-500/20">
          K
        </div>
        <div>
          <h1 className="text-white font-bold tracking-wide text-base m-0">KALNET AI</h1>
          <p className="text-[10px] text-slate-500 font-medium m-0 uppercase tracking-wider">Intelligent Outreach</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group cursor-pointer ${
                isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/10'
                  : 'hover:bg-slate-800 hover:text-white text-slate-400'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className={`transition-colors duration-150 ${
                  isActive ? 'text-white' : 'text-slate-500 group-hover:text-slate-300'
                }`}>
                  <Icon className="w-5 h-5" />
                </span>
                <span>{item.label}</span>
              </div>
              
              {item.badge && (
                <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${
                  isActive 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-blue-900/30 text-blue-400 border border-blue-800/20'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
