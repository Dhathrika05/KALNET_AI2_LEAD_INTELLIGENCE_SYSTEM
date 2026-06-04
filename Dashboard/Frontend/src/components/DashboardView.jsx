import React, { useState, useMemo } from 'react';
import {
  SearchIcon,
  DownloadIcon,
  FilterIcon,
  SpinnerIcon,
  AlertCircleIcon,
  ChevronDownIcon,
  ChevronRightIcon
} from './Icons';

export default function DashboardView({
  leads,
  loading,
  error,
  fetchLeads,
  searchTerm,
  setSearchTerm,
  selectedState,
  setSelectedState,
  selectedType,
  setSelectedType,
  selectedTier,
  setSelectedTier,
  selectedHasEmail,
  setSelectedHasEmail
}) {
  // Local state for expanded rows
  const [expandedRows, setExpandedRows] = useState({});

  // Toggle row expansion
  const toggleRow = (id) => {
    setExpandedRows(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  // 1. Dynamically extract filter options from fetched database records
  const filterOptions = useMemo(() => {
    const statesSet = new Set();
    const typesSet = new Set();
    const tiersSet = new Set();

    leads.forEach(lead => {
      if (lead.state) statesSet.add(lead.state.trim());
      if (lead.type) typesSet.add(lead.type.trim());
      
      const tierVal = lead.icp_tier || lead.tier;
      if (tierVal) tiersSet.add(tierVal.trim());
    });

    return {
      states: Array.from(statesSet).sort(),
      types: Array.from(typesSet).sort(),
      tiers: Array.from(tiersSet).sort()
    };
  }, [leads]);

  // 2. Perform local in-memory filtering of leads based on user query
  const filteredLeads = useMemo(() => {
    return leads.filter(lead => {
      // A. Text Search filter: check multiple fields
      if (searchTerm.trim() !== '') {
        const query = searchTerm.toLowerCase();
        const name = (lead.name || '').toLowerCase();
        const district = (lead.district || '').toLowerCase();
        const state = (lead.state || '').toLowerCase();
        const principal = (lead.principal_name || '').toLowerCase();
        const website = (lead.website || '').toLowerCase();
        const companySize = (lead.company_size_category || '').toLowerCase();
        const email = (lead.email || '').toLowerCase();
        
        const matches = 
          name.includes(query) || 
          district.includes(query) || 
          state.includes(query) || 
          principal.includes(query) || 
          website.includes(query) ||
          companySize.includes(query) ||
          email.includes(query);
          
        if (!matches) return false;
      }

      // B. State filter
      if (selectedState && lead.state !== selectedState) {
        return false;
      }

      // C. Institution Type filter
      if (selectedType && lead.type !== selectedType) {
        return false;
      }

      // D. ICP Tier filter
      const leadTier = lead.icp_tier || lead.tier;
      if (selectedTier && leadTier !== selectedTier) {
        return false;
      }

      // E. Has Email filter
      if (selectedHasEmail && (!lead.email || lead.email.trim() === '')) {
        return false;
      }

      return true;
    });
  }, [leads, searchTerm, selectedState, selectedType, selectedTier, selectedHasEmail]);

  // CSV Exporter (Exports the filtered data!)
  const handleDownloadCSV = () => {
    if (filteredLeads.length === 0) return;

    // Define all 14 schema columns to export
    const headers = [
      'id', 'name', 'state', 'district', 'type', 'board', 
      'student_count', 'company_size_category', 'website', 
      'principal_name', 'email', 'phone', 'icp_score', 'icp_tier'
    ];
    
    const csvRows = [];
    
    // Add headers
    csvRows.push(headers.join(','));
    
    // Add records
    for (const lead of filteredLeads) {
      const values = headers.map(header => {
        let val = lead[header];
        if (header === 'icp_tier' && val === undefined) {
          val = lead['tier']; // handle alias
        }
        const valStr = val === null || val === undefined ? '' : String(val);
        // Escape double quotes by doubling them, wrap in quotes
        const escaped = valStr.replace(/"/g, '""');
        return `"${escaped}"`;
      });
      csvRows.push(values.join(','));
    }

    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `kalnet_filtered_leads_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Calculate dynamic metrics based on filtered leads
  const metrics = useMemo(() => {
    const total = filteredLeads.length;
    const withEmail = filteredLeads.filter(l => l.email && l.email.trim() !== '').length;
    
    // Average Student Count
    const studentLeads = filteredLeads.filter(l => l.student_count !== null && l.student_count !== undefined && String(l.student_count).trim() !== '');
    const sumStudents = studentLeads.reduce((acc, l) => acc + Number(l.student_count), 0);
    const avgStudents = studentLeads.length ? Math.round(sumStudents / studentLeads.length) : 0;
    
    // Unique States Count
    const uniqueStates = new Set(filteredLeads.map(l => l.state).filter(Boolean));
    const statesCount = uniqueStates.size;

    return {
      total,
      withEmail,
      avgStudents,
      statesCount
    };
  }, [filteredLeads]);

  const handleResetFilters = () => {
    setSearchTerm('');
    setSelectedState('');
    setSelectedType('');
    setSelectedTier('');
    setSelectedHasEmail(false);
  };

  return (
    <div className="space-y-6">
      {/* Search & Filter Form Card */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <FilterIcon className="w-5 h-5 text-blue-600" />
            <h2 className="text-base font-bold text-slate-800 m-0">Dynamic Filters</h2>
          </div>
          <button
            type="button"
            onClick={handleResetFilters}
            className="text-xs font-semibold text-slate-500 hover:text-blue-600 transition-colors cursor-pointer"
          >
            Reset Filters
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* Real-time Search Input */}
          <div className="flex flex-col gap-1.5">
            <label htmlFor="search" className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Search Filtered Data
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400 pointer-events-none">
                <SearchIcon className="w-4 h-4" />
              </span>
              <input
                id="search"
                type="text"
                placeholder="Type to filter rows..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 focus:border-blue-500 focus:bg-white rounded-lg pl-9 pr-3 py-2 text-sm text-slate-800 outline-none transition-all placeholder-slate-400"
              />
            </div>
          </div>

          {/* Dynamic State Select */}
          <div className="flex flex-col gap-1.5">
            <label htmlFor="state" className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              State ({filterOptions.states.length} available)
            </label>
            <select
              id="state"
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 focus:border-blue-500 focus:bg-white rounded-lg px-3 py-2 text-sm text-slate-800 outline-none transition-all cursor-pointer"
            >
              <option value="">All States</option>
              {filterOptions.states.map((opt, idx) => (
                <option key={idx} value={opt}>{opt}</option>
              ))}
            </select>
          </div>

          {/* Dynamic School Type Select */}
          <div className="flex flex-col gap-1.5">
            <label htmlFor="schoolType" className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Institution Type
            </label>
            <select
              id="schoolType"
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 focus:border-blue-500 focus:bg-white rounded-lg px-3 py-2 text-sm text-slate-800 outline-none transition-all cursor-pointer"
            >
              <option value="">All Types</option>
              {filterOptions.types.map((opt, idx) => (
                <option key={idx} value={opt}>{opt}</option>
              ))}
            </select>
          </div>

          {/* Dynamic Tier Select */}
          <div className="flex flex-col gap-1.5">
            <label htmlFor="tier" className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              ICP Tier
            </label>
            <select
              id="tier"
              value={selectedTier}
              onChange={(e) => setSelectedTier(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 focus:border-blue-500 focus:bg-white rounded-lg px-3 py-2 text-sm text-slate-800 outline-none transition-all cursor-pointer"
            >
              <option value="">All Tiers</option>
              {filterOptions.tiers.map((opt, idx) => (
                <option key={idx} value={opt}>{opt}</option>
              ))}
            </select>
          </div>

        </div>

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pt-4 mt-2 border-t border-slate-100 gap-4">
          {/* Email Checkbox */}
          <label className="inline-flex items-center gap-2.5 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={selectedHasEmail}
              onChange={(e) => setSelectedHasEmail(e.target.checked)}
              className="w-4.5 h-4.5 text-blue-600 border-slate-300 rounded focus:ring-blue-500 bg-slate-50 cursor-pointer"
            />
            <span className="text-sm font-semibold text-slate-600">
              Only show leads with email address
            </span>
          </label>

          <div className="text-xs text-slate-400 font-medium">
            Showing {filteredLeads.length} of {leads.length} leads in database
          </div>
        </div>
      </div>

      {/* API Error alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <span className="text-red-500 mt-0.5">
            <AlertCircleIcon className="w-5 h-5" />
          </span>
          <div>
            <h4 className="text-sm font-bold text-red-800 m-0">Server Sync Error</h4>
            <p className="text-xs text-red-700 m-1">{error}</p>
            <button
              onClick={fetchLeads}
              className="mt-2 text-xs font-bold text-red-800 underline hover:text-red-900 cursor-pointer"
            >
              Retry Connection
            </button>
          </div>
        </div>
      )}

      {/* Summary Cards Section */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Total Leads */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider m-0">Total Leads</p>
          <h3 className="text-3xl font-black text-blue-600 m-0 mt-1 select-none">
            {metrics.total.toLocaleString()}
          </h3>
        </div>

        {/* With Email */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider m-0">With Email</p>
          <h3 className="text-3xl font-black text-slate-800 m-0 mt-1 select-none">
            {metrics.withEmail.toLocaleString()}
          </h3>
        </div>

        {/* Avg Students */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider m-0">Avg Students</p>
          <h3 className="text-3xl font-black text-slate-800 m-0 mt-1 select-none">
            {metrics.avgStudents.toLocaleString()}
          </h3>
        </div>

        {/* States */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider m-0">States</p>
          <h3 className="text-3xl font-black text-slate-800 m-0 mt-1 select-none">
            {metrics.statesCount}
          </h3>
        </div>

      </div>

      {/* Main Leads Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div>
            <h3 className="text-sm font-bold text-slate-800 m-0">Institution Lead Registry</h3>
            <p className="text-xs text-slate-500 m-0">Displaying all 14 schema fields. Click rows to expand details.</p>
          </div>

          {filteredLeads.length > 0 && (
            <button
              onClick={handleDownloadCSV}
              className="flex items-center justify-center gap-2 px-8 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition-all cursor-pointer shadow-sm shadow-blue-500/10 min-w-[200px]"
            >
              <DownloadIcon className="w-4 h-4" />
              Download CSV ({filteredLeads.length} rows)
            </button>
          )}
        </div>

        <div className="relative min-h-[300px]">
          {loading && leads.length === 0 && (
            <div className="absolute inset-0 bg-white/80 flex flex-col items-center justify-center gap-3 z-10">
              <SpinnerIcon className="w-8 h-8 text-blue-600" />
              <p className="text-xs font-semibold text-slate-500 animate-pulse">Contacting database...</p>
            </div>
          )}

          {filteredLeads.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse table-fixed min-w-[2200px]">
                <thead>
                  <tr className="bg-slate-50/75 border-b border-slate-150">
                    <th className="w-12 px-6 py-3.5"></th>
                    <th className="w-16 px-6 py-3.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">ID</th>
                    <th className="w-72 px-6 py-3.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Institution Name</th>
                    <th className="w-40 px-6 py-3.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">State</th>
                    <th className="w-40 px-6 py-3.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">District</th>
                    <th className="w-28 px-6 py-3.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Type</th>
                    <th className="w-28 px-6 py-3.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Board</th>
                    <th className="w-36 px-6 py-3.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Student Count</th>
                    <th className="w-44 px-6 py-3.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Company Size</th>
                    <th className="w-56 px-6 py-3.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Website</th>
                    <th className="w-48 px-6 py-3.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Principal Name</th>
                    <th className="w-60 px-6 py-3.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Email Address</th>
                    <th className="w-40 px-6 py-3.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Phone Number</th>
                    <th className="w-28 px-6 py-3.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">ICP Score</th>
                    <th className="w-28 px-6 py-3.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">ICP Tier</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredLeads.map((lead) => {
                    const isExpanded = !!expandedRows[lead.id];
                    const tierVal = lead.icp_tier || lead.tier;
                    
                    return (
                      <React.Fragment key={lead.id}>
                        {/* Table Row */}
                        <tr 
                          onClick={() => toggleRow(lead.id)}
                          className={`hover:bg-slate-50/70 transition-colors cursor-pointer select-none ${
                            isExpanded ? 'bg-slate-50/40' : ''
                          }`}
                        >
                          <td className="px-6 py-4 text-center">
                            {isExpanded ? (
                              <ChevronDownIcon className="w-4 h-4 text-slate-400" />
                            ) : (
                              <ChevronRightIcon className="w-4 h-4 text-slate-400" />
                            )}
                          </td>
                          <td className="px-6 py-4 text-xs font-semibold text-slate-400">{lead.id}</td>
                          <td className="px-6 py-4 text-xs font-bold text-slate-800 truncate" title={lead.name}>
                            {lead.name}
                          </td>
                          <td className="px-6 py-4 text-xs text-slate-600 truncate">{lead.state || '-'}</td>
                          <td className="px-6 py-4 text-xs text-slate-600 truncate">{lead.district || '-'}</td>
                          <td className="px-6 py-4 text-xs">
                            {lead.type ? (
                              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                lead.type.toLowerCase() === 'govt' 
                                  ? 'bg-slate-100 text-slate-700 border border-slate-200' 
                                  : 'bg-indigo-50 text-indigo-700 border border-indigo-150'
                              }`}>
                                {lead.type}
                              </span>
                            ) : '-'}
                          </td>
                          <td className="px-6 py-4 text-xs text-slate-600 truncate">{lead.board || '-'}</td>
                          <td className="px-6 py-4 text-xs font-semibold text-slate-700">
                            {lead.student_count !== null && lead.student_count !== undefined ? lead.student_count.toLocaleString() : '-'}
                          </td>
                          <td className="px-6 py-4 text-xs text-slate-600 truncate">{lead.company_size_category || '-'}</td>
                          <td className="px-6 py-4 text-xs text-slate-600 truncate">
                            {lead.website ? (
                              <a 
                                href={lead.website.startsWith('http') ? lead.website : `https://${lead.website}`} 
                                target="_blank" 
                                rel="noreferrer" 
                                onClick={(e) => e.stopPropagation()} 
                                className="text-blue-600 hover:underline font-semibold"
                              >
                                {lead.website}
                              </a>
                            ) : '-'}
                          </td>
                          <td className="px-6 py-4 text-xs text-slate-600 truncate">{lead.principal_name || '-'}</td>
                          <td className="px-6 py-4 text-xs font-medium text-slate-600 truncate">
                            {lead.email ? (
                              <a 
                                href={`mailto:${lead.email}`} 
                                onClick={(e) => e.stopPropagation()} 
                                className="text-blue-600 hover:text-blue-750 underline"
                              >
                                {lead.email}
                              </a>
                            ) : (
                              <span className="text-slate-400 italic">None</span>
                            )}
                          </td>
                          <td className="px-6 py-4 text-xs text-slate-600 truncate">{lead.phone || '-'}</td>
                          <td className="px-6 py-4 text-xs font-bold text-slate-700">
                            {lead.icp_score !== null && lead.icp_score !== undefined ? lead.icp_score : '-'}
                          </td>
                          <td className="px-6 py-4 text-xs">
                            {tierVal ? (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-150">
                                {tierVal}
                              </span>
                            ) : '-'}
                          </td>
                        </tr>

                        {/* Expandable Details Panel showing all 14 fields */}
                        {isExpanded && (
                          <tr>
                            <td colSpan={15} className="bg-slate-50/50 px-8 py-5 border-t border-b border-slate-200/80">
                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 text-xs">
                                
                                <div>
                                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                                    Institution Details
                                  </span>
                                  <div className="space-y-1 bg-white p-3 rounded-lg border border-slate-150">
                                    <p className="m-0"><strong className="text-slate-600">ID:</strong> {lead.id}</p>
                                    <p className="m-0"><strong className="text-slate-600">Name:</strong> {lead.name}</p>
                                    <p className="m-0"><strong className="text-slate-600">Type:</strong> {lead.type || 'N/A'}</p>
                                    <p className="m-0"><strong className="text-slate-600">Board:</strong> {lead.board || 'N/A'}</p>
                                  </div>
                                </div>

                                <div>
                                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                                    Geography
                                  </span>
                                  <div className="space-y-1 bg-white p-3 rounded-lg border border-slate-150">
                                    <p className="m-0"><strong className="text-slate-600">District:</strong> {lead.district || 'N/A'}</p>
                                    <p className="m-0"><strong className="text-slate-600">State:</strong> {lead.state || 'N/A'}</p>
                                    <p className="m-0"><strong className="text-slate-600">Website:</strong> {lead.website ? (
                                      <a href={lead.website.startsWith('http') ? lead.website : `https://${lead.website}`} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">
                                        {lead.website}
                                      </a>
                                    ) : 'N/A'}</p>
                                  </div>
                                </div>

                                <div>
                                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                                    Contacts
                                  </span>
                                  <div className="space-y-1 bg-white p-3 rounded-lg border border-slate-150">
                                    <p className="m-0"><strong className="text-slate-600">Principal:</strong> {lead.principal_name || 'N/A'}</p>
                                    <p className="m-0"><strong className="text-slate-600">Email:</strong> {lead.email || 'N/A'}</p>
                                    <p className="m-0"><strong className="text-slate-600">Phone:</strong> {lead.phone || 'N/A'}</p>
                                  </div>
                                </div>

                                <div>
                                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                                    Lead Analytics
                                  </span>
                                  <div className="space-y-1 bg-white p-3 rounded-lg border border-slate-150">
                                    <p className="m-0"><strong className="text-slate-600">Student Count:</strong> {lead.student_count !== null && lead.student_count !== undefined ? lead.student_count.toLocaleString() : 'N/A'}</p>
                                    <p className="m-0"><strong className="text-slate-600">Company Size:</strong> {lead.company_size_category || 'N/A'}</p>
                                    <p className="m-0"><strong className="text-slate-600">ICP Score:</strong> {lead.icp_score !== null && lead.icp_score !== undefined ? lead.icp_score : 'N/A'}</p>
                                    <p className="m-0"><strong className="text-slate-600">ICP Tier:</strong> {tierVal || 'N/A'}</p>
                                  </div>
                                </div>

                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-20 px-6 flex flex-col items-center justify-center text-center">
              <SearchIcon className="w-10 h-10 text-slate-300 mb-3" />
              <h4 className="text-sm font-bold text-slate-700 m-0">No matching leads</h4>
              <p className="text-xs text-slate-500 max-w-sm mt-1 mb-0">
                Adjust search keywords or dropdown selections.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
