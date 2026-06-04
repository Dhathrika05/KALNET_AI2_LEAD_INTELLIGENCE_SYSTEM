import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import DashboardView from './components/DashboardView';
import UploaderView from './components/UploaderView';
import AnalyticsView from './components/AnalyticsView';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Lifted filter states to prevent data loss on tab switching
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedState, setSelectedState] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedTier, setSelectedTier] = useState('');
  const [selectedHasEmail, setSelectedHasEmail] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || 'https://kalnet-dashboard-api-3.onrender.com/leads';

  // Fetch leads from database
  const fetchLeads = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(API_URL, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`API returned status code ${response.status}`);
      }

      const resData = await response.json();
      if (resData.error) {
        throw new Error(resData.error);
      }

      setLeads(resData.message || []);
    } catch (err) {
      console.error('Fetch error:', err);
      setError(err.message || 'Could not connect to database API');
    } finally {
      setLoading(false);
    }
  };

  // Fetch data on initial mount
  useEffect(() => {
    fetchLeads();
  }, []);

  const headerContent = {
    dashboard: {
      title: 'Outreach Dashboard',
      description: 'Filter leads, search fetched records in real-time, and download your target outreach datasets.'
    },
    uploader: {
      title: 'CSV Data Importer',
      description: 'Upload CSV lists to parse, preview, and insert new institution leads directly into the database.'
    },
    analytics: {
      title: 'Campaign Analytics',
      description: 'Visualize your lead demographics, tier distributions, and school types with real-time graphs.'
    }
  };

  const currentHeader = headerContent[activeTab] || {
    title: 'Kalnet AI System',
    description: 'Intelligent Outreach System'
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <DashboardView
            leads={leads}
            loading={loading}
            error={error}
            fetchLeads={fetchLeads}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            selectedState={selectedState}
            setSelectedState={setSelectedState}
            selectedType={selectedType}
            setSelectedType={setSelectedType}
            selectedTier={selectedTier}
            setSelectedTier={setSelectedTier}
            selectedHasEmail={selectedHasEmail}
            setSelectedHasEmail={setSelectedHasEmail}
          />
        );
      case 'uploader':
        return (
          <UploaderView
            onUploadSuccess={fetchLeads}
          />
        );
      case 'analytics':
        return (
          <AnalyticsView
            leads={leads}
            loading={loading}
          />
        );
      default:
        return (
          <div className="bg-white border border-slate-200 rounded-xl p-8 text-center max-w-xl mx-auto my-12">
            <h3 className="text-base font-bold text-slate-800 m-0">View Not Found</h3>
            <button
              onClick={() => setActiveTab('dashboard')}
              className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm cursor-pointer transition-all"
            >
              Back to Dashboard
            </button>
          </div>
        );
    }
  };

  return (
    <div className="flex bg-slate-50 text-slate-900 min-h-screen">
      {/* Sidebar navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top Header Bar */}
        <header className="bg-white border-b border-slate-200/80 px-8 py-5 flex items-center justify-between z-10">
          <div>
            <h2 className="text-lg font-bold text-slate-900 m-0 select-none">
              {currentHeader.title}
            </h2>
            <p className="text-xs text-slate-500 m-0 mt-0.5 select-none max-w-2xl leading-relaxed">
              {currentHeader.description}
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            {loading ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-100">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
                Synchronizing Database...
              </span>
            ) : error ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-100">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500"></span>
                Database Offline
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-100">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                Database Synced ({leads.length} leads)
              </span>
            )}
          </div>
        </header>

        {/* Content View Scroll Container */}
        <main className="flex-1 overflow-y-auto px-8 py-6">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

export default App;
