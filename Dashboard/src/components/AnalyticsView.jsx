import React, { useMemo } from 'react';
import { SpinnerIcon, AnalyticsIcon } from './Icons';

export default function AnalyticsView({ leads, loading }) {
  
  // Calculate summary metrics
  const stats = useMemo(() => {
    const total = leads.length;
    let govt = 0;
    let privateType = 0;
    let tier1 = 0;
    let tier2 = 0;
    let tier3 = 0;
    let totalScore = 0;
    let hasScoreCount = 0;
    let totalStudents = 0;
    let hasStudentsCount = 0;

    leads.forEach(l => {
      // Type breakdown
      const typeStr = (l.type || '').toLowerCase();
      if (typeStr === 'govt') govt++;
      else if (typeStr === 'private') privateType++;

      // Tier breakdown
      const tierStr = (l.icp_tier || l.tier || '').toLowerCase();
      if (tierStr === 'tier1') tier1++;
      else if (tierStr === 'tier2') tier2++;
      else if (tierStr === 'tier3') tier3++;

      // Average ICP Score
      if (l.icp_score !== null && l.icp_score !== undefined) {
        totalScore += Number(l.icp_score);
        hasScoreCount++;
      }

      // Total Students
      if (l.student_count !== null && l.student_count !== undefined) {
        totalStudents += Number(l.student_count);
        hasStudentsCount++;
      }
    });

    const avgScore = hasScoreCount ? Math.round(totalScore / hasScoreCount) : 0;
    const avgStudents = hasStudentsCount ? Math.round(totalStudents / hasStudentsCount) : 0;

    return {
      total,
      govt,
      private: privateType,
      tier1,
      tier2,
      tier3,
      avgScore,
      avgStudents
    };
  }, [leads]);

  // Extract State counts for visualization
  const stateChartData = useMemo(() => {
    const stateCounts = {};
    leads.forEach(l => {
      if (l.state) {
        const stateName = l.state.trim();
        stateCounts[stateName] = (stateCounts[stateName] || 0) + 1;
      }
    });

    // Convert to sorted array of objects
    return Object.keys(stateCounts)
      .map(state => ({ name: state, count: stateCounts[state] }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5); // top 5 states
  }, [leads]);

  // Render SVG Vertical Bar Chart for States
  const renderStateChart = () => {
    if (stateChartData.length === 0) return null;

    const chartHeight = 160;
    const chartWidth = 460;
    const maxCount = Math.max(...stateChartData.map(d => d.count), 1);
    const colWidth = 60;
    const spacing = 25;
    const startX = 40;

    return (
      <svg className="w-full h-48 mt-4" viewBox="0 0 500 220" fill="none">
        {/* Horizontal Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio, idx) => {
          const y = chartHeight - ratio * chartHeight + 20;
          const labelVal = Math.round(ratio * maxCount);
          return (
            <g key={idx}>
              <line x1="30" y1={y} x2="480" y2={y} stroke="#f1f5f9" strokeWidth="1" />
              <text x="5" y={y + 4} fill="#94a3b8" fontSize="10" className="font-semibold">{labelVal}</text>
            </g>
          );
        })}

        {/* Bars */}
        {stateChartData.map((data, idx) => {
          const x = startX + idx * (colWidth + spacing);
          const barHeight = (data.count / maxCount) * chartHeight;
          const y = chartHeight - barHeight + 20;

          return (
            <g key={idx} className="group">
              {/* Rounded Bar */}
              <rect
                x={x}
                y={y}
                width={colWidth}
                height={Math.max(barHeight, 4)} // at least 4px height
                rx="4"
                className="fill-blue-600/85 hover:fill-blue-600 transition-colors duration-150 cursor-pointer"
              />
              
              {/* Count Text on top of Bar */}
              <text
                x={x + colWidth / 2}
                y={y - 6}
                fill="#334155"
                fontSize="11"
                fontWeight="bold"
                textAnchor="middle"
              >
                {data.count}
              </text>

              {/* State label below axis */}
              <text
                x={x + colWidth / 2}
                y={chartHeight + 38}
                fill="#64748b"
                fontSize="10"
                fontWeight="semibold"
                textAnchor="middle"
                className="truncate"
              >
                {data.name.length > 10 ? `${data.name.slice(0, 8)}..` : data.name}
              </text>
            </g>
          );
        })}
      </svg>
    );
  };

  if (loading && leads.length === 0) {
    return (
      <div className="py-24 flex flex-col items-center justify-center bg-white rounded-xl border border-slate-200">
        <SpinnerIcon className="w-8 h-8 text-blue-600 mb-3" />
        <p className="text-xs font-semibold text-slate-500">Generating analytics dashboard...</p>
      </div>
    );
  }

  if (leads.length === 0) {
    return (
      <div className="py-24 text-center bg-white rounded-xl border border-slate-200">
        <AnalyticsIcon className="w-10 h-10 text-slate-300 mx-auto mb-3" />
        <h4 className="text-sm font-bold text-slate-700 m-0">No lead data to analyze</h4>
        <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-0">
          Upload some data using the CSV Uploader to populate the metrics and visualizations.
        </p>
      </div>
    );
  }

  // Calculate percentages for breakdown charts
  const govtPercent = stats.total ? Math.round((stats.govt / stats.total) * 100) : 0;
  const privatePercent = stats.total ? Math.round((stats.private / stats.total) * 100) : 0;
  
  const tier1Percent = stats.total ? Math.round((stats.tier1 / stats.total) * 100) : 0;
  const tier2Percent = stats.total ? Math.round((stats.tier2 / stats.total) * 100) : 0;
  const tier3Percent = stats.total ? Math.round((stats.tier3 / stats.total) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Total Leads */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs flex items-center gap-4">
          <div className="w-11 h-11 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider m-0">Total Leads</p>
            <h3 className="text-xl font-black text-slate-800 m-0 mt-0.5">{stats.total.toLocaleString()}</h3>
          </div>
        </div>

        {/* Govt vs Private Ratio */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs flex items-center gap-4">
          <div className="w-11 h-11 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider m-0">Govt / Private</p>
            <h3 className="text-xl font-black text-slate-800 m-0 mt-0.5">{stats.govt} / {stats.private}</h3>
          </div>
        </div>

        {/* Tier 1 Leads */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs flex items-center gap-4">
          <div className="w-11 h-11 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider m-0">Tier 1 Leads</p>
            <h3 className="text-xl font-black text-slate-800 m-0 mt-0.5">{stats.tier1.toLocaleString()}</h3>
          </div>
        </div>

        {/* Avg ICP Score */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs flex items-center gap-4">
          <div className="w-11 h-11 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider m-0">Avg ICP Score</p>
            <h3 className="text-xl font-black text-slate-800 m-0 mt-0.5">{stats.avgScore} / 100</h3>
          </div>
        </div>

      </div>

      {/* Visualizations row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* State-wise Distribution Card */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-800 m-0">Top States by Lead Count</h3>
            <p className="text-xs text-slate-400 m-0 mt-0.5">Visualization of lead volume in the top 5 states</p>
          </div>
          <div className="flex-1 flex items-center justify-center">
            {stateChartData.length > 0 ? renderStateChart() : (
              <p className="text-xs text-slate-400 py-8">State data unavailable</p>
            )}
          </div>
        </div>

        {/* Segment breakdowns */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs space-y-6">
          <div>
            <h3 className="text-sm font-bold text-slate-800 m-0">Outreach Segment Analysis</h3>
            <p className="text-xs text-slate-400 m-0 mt-0.5">Distribution breakdown across ICP tiers and institution types</p>
          </div>

          {/* ICP Tiers horizontal bar distribution */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-700 m-0 uppercase tracking-wider">ICP TIER SEGMENTATION</h4>
            
            <div className="space-y-2.5">
              {/* Tier 1 Progress */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-600">Tier 1 (High Quality)</span>
                  <span className="text-slate-800 font-bold">{stats.tier1} ({tier1Percent}%)</span>
                </div>
                <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-600 rounded-full transition-all" style={{ width: `${tier1Percent}%` }}></div>
                </div>
              </div>

              {/* Tier 2 Progress */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-600">Tier 2 (Medium Quality)</span>
                  <span className="text-slate-800 font-bold">{stats.tier2} ({tier2Percent}%)</span>
                </div>
                <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full transition-all" style={{ width: `${tier2Percent}%` }}></div>
                </div>
              </div>

              {/* Tier 3 Progress */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-600">Tier 3 (Standard)</span>
                  <span className="text-slate-800 font-bold">{stats.tier3} ({tier3Percent}%)</span>
                </div>
                <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-slate-400 rounded-full transition-all" style={{ width: `${tier3Percent}%` }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Institution Types comparative progress bars */}
          <div className="space-y-3 pt-3 border-t border-slate-100">
            <h4 className="text-xs font-bold text-slate-700 m-0 uppercase tracking-wider">INSTITUTION TYPE SEGMENTATION</h4>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-50 border border-slate-150 p-4 rounded-xl text-center space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Government</span>
                <h4 className="text-lg font-black text-slate-800 m-0">{stats.govt}</h4>
                <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full inline-block">
                  {govtPercent}% of total
                </span>
              </div>

              <div className="bg-slate-50 border border-slate-150 p-4 rounded-xl text-center space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Private</span>
                <h4 className="text-lg font-black text-slate-800 m-0">{stats.private}</h4>
                <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full inline-block">
                  {privatePercent}% of total
                </span>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
