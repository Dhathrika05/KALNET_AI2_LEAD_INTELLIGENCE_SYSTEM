import React, { useState, useRef } from 'react';
import {
  UploadIcon,
  CheckCircleIcon,
  AlertCircleIcon,
  SpinnerIcon,
  CloseIcon
} from './Icons';

export default function UploaderView({ onUploadSuccess }) {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const API_URL = import.meta.env.VITE_API_URL || 'https://kalnet-dashboard-api-3.onrender.com/leads';

  // Helper: Parse CSV content
  const parseCSV = (text) => {
    const lines = text.split(/\r?\n/);
    if (lines.length === 0 || !lines[0].trim()) {
      return { headers: [], rows: [] };
    }

    // Helper: Split CSV line respecting quotes
    const parseCSVLine = (line) => {
      const result = [];
      let current = '';
      let inQuotes = false;
      for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"') {
          inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
          result.push(current.trim());
          current = '';
        } else {
          current += char;
        }
      }
      result.push(current.trim());
      // Strip wrapping double quotes
      return result.map(val => val.replace(/^"|"$/g, '').trim());
    };

    const rawHeaders = parseCSVLine(lines[0]);
    // Clean headers for mapping
    const headers = rawHeaders.map(h => h.trim());
    const rows = [];

    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;
      
      const values = parseCSVLine(line);
      const row = {};
      headers.forEach((header, index) => {
        row[header] = values[index] || '';
      });
      rows.push(row);
    }

    return { headers, rows };
  };

  // Handle Drag & Drop events
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const processFile = (selectedFile) => {
    if (!selectedFile) return;

    if (selectedFile.type !== "text/csv" && !selectedFile.name.endsWith('.csv')) {
      setError("Invalid file type. Please upload a CSV file (.csv).");
      setFile(null);
      setParsedData(null);
      return;
    }

    setError(null);
    setUploadStatus(null);
    setFile(selectedFile);

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      const parsed = parseCSV(text);
      setParsedData(parsed);
    };
    reader.onerror = () => {
      setError("Failed to read the file. Please try again.");
    };
    reader.readAsText(selectedFile);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const clearFile = () => {
    setFile(null);
    setParsedData(null);
    setUploadStatus(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // Perform upload to FastAPI
  const handleUpload = async () => {
    if (!file || !parsedData) return;

    setUploading(true);
    setError(null);
    setUploadStatus(null);

    // Method A: Multipart Form Data (Sending the File object)
    const formData = new FormData();
    formData.append('file', file);

    try {
      let response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
        // Let fetch set the boundary header automatically for FormData
      });

      // Method B Fallback: If Method A gets rejected (e.g. CORS or method unsupported),
      // we try sending the parsed records as JSON.
      if (!response.ok) {
        console.warn(`File upload returned status ${response.status}. Attempting JSON upload fallback...`);
        
        // Map headers to DB compatible properties:
        // school_name/institution_name/search -> name
        // school_type -> type
        // tier -> icp_tier
        const dbMappedLeads = parsedData.rows.map(row => {
          const mapped = {};
          Object.keys(row).forEach(key => {
            const lowerKey = key.toLowerCase().replace(/[\s_-]/g, '');
            if (['name', 'schoolname', 'institutionname', 'search'].includes(lowerKey)) {
              mapped['name'] = row[key];
            } else if (['district', 'dist'].includes(lowerKey)) {
              mapped['district'] = row[key];
            } else if (['state'].includes(lowerKey)) {
              mapped['state'] = row[key];
            } else if (['type', 'schooltype'].includes(lowerKey)) {
              mapped['type'] = row[key];
            } else if (['tier', 'icptier'].includes(lowerKey)) {
              mapped['icp_tier'] = row[key];
            } else if (['email', 'emailaddress'].includes(lowerKey)) {
              mapped['email'] = row[key];
            } else {
              // keep as is
              mapped[key] = row[key];
            }
          });
          return mapped;
        });

        response = await fetch(API_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify(dbMappedLeads)
        });
      }

      if (!response.ok) {
        throw new Error(`Server returned error code ${response.status}: ${response.statusText}`);
      }

      const resData = await response.json();
      
      if (resData.error) {
        throw new Error(resData.error);
      }

      setUploadStatus({
        type: 'success',
        message: resData.message || `Successfully imported dataset into database.`
      });

      if (onUploadSuccess) {
        onUploadSuccess();
      }
      
      // Clear file after successful upload
      setFile(null);
      setParsedData(null);
    } catch (err) {
      console.error('Upload failed:', err);
      setError(err.message || 'Could not connect to backend server for upload');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* CSV Upload Form */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm p-6">
        <h2 className="text-base font-bold text-slate-800 mb-1">CSV Data Importer</h2>
        <p className="text-xs text-slate-500 mb-5">
          Select or drag and drop a CSV file containing institution leads to insert them directly into the database.
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4 mb-4 flex items-start gap-3">
            <span className="text-red-500 mt-0.5">
              <AlertCircleIcon className="w-5 h-5" />
            </span>
            <div>
              <p className="text-xs font-semibold m-0">{error}</p>
            </div>
          </div>
        )}

        {uploadStatus && uploadStatus.type === 'success' && (
          <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg p-4 mb-4 flex items-start gap-3">
            <span className="text-emerald-500 mt-0.5">
              <CheckCircleIcon className="w-5 h-5" />
            </span>
            <div>
              <p className="text-xs font-semibold m-0">{uploadStatus.message}</p>
            </div>
          </div>
        )}

        {!file ? (
          /* Drag and Drop Zone */
          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current.click()}
            className={`border-2 border-dashed rounded-xl py-12 px-6 text-center cursor-pointer transition-all flex flex-col items-center justify-center ${
              dragActive 
                ? 'border-blue-500 bg-blue-50/40' 
                : 'border-slate-300 hover:border-blue-400 bg-slate-50/50 hover:bg-slate-50'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
            />
            <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
              <UploadIcon className="w-6 h-6" />
            </div>
            <p className="text-sm font-bold text-slate-700 m-0">Click to upload or drag and drop</p>
            <p className="text-xs text-slate-500 mt-1 mb-0">CSV files only (.csv)</p>
          </div>
        ) : (
          /* File Selected State */
          <div className="border border-slate-200 rounded-xl p-4 bg-slate-50/50 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xs">
                CSV
              </div>
              <div>
                <p className="text-sm font-bold text-slate-800 m-0">{file.name}</p>
                <p className="text-xs text-slate-400 m-0">{(file.size / 1024).toFixed(1)} KB • {parsedData?.rows?.length || 0} rows found</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleUpload}
                disabled={uploading || !parsedData}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-xs font-semibold rounded-lg shadow-sm flex items-center gap-2 transition-all cursor-pointer"
              >
                {uploading ? (
                  <>
                    <SpinnerIcon className="w-3.5 h-3.5 text-white" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <UploadIcon className="w-3.5 h-3.5" />
                    Upload Leads
                  </>
                )}
              </button>
              
              <button
                onClick={clearFile}
                disabled={uploading}
                className="p-2 border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-50 text-slate-500 hover:text-slate-700 rounded-lg transition-all cursor-pointer"
              >
                <CloseIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* CSV Parser Preview Table */}
      {parsedData && parsedData.rows.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50">
            <h3 className="text-sm font-bold text-slate-800 m-0">CSV File Preview</h3>
            <p className="text-xs text-slate-500 m-0">Showing first 10 rows for structure verification</p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/75 border-b border-slate-150">
                  {parsedData.headers.map((header, idx) => (
                    <th key={idx} className="px-6 py-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {parsedData.rows.slice(0, 10).map((row, rowIdx) => (
                  <tr key={rowIdx} className="hover:bg-slate-50/30">
                    {parsedData.headers.map((header, colIdx) => (
                      <td key={colIdx} className="px-6 py-3 text-xs text-slate-600 truncate max-w-xs">
                        {row[header] !== undefined ? String(row[header]) : ''}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
