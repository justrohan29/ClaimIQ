import React, { useState } from 'react';
import { UploadCloud, Zap, ShieldCheck, FileText, ArrowRight, Activity, X } from 'lucide-react';

export default function UploadZone({ onStartDemo, onUploadFiles, isUploading }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);

  const addFiles = (newFiles) => {
    setSelectedFiles((prev) => {
      const existingNames = new Set(prev.map((f) => f.name));
      const added = newFiles.filter((f) => !existingNames.has(f.name));
      return [...prev, ...added];
    });
  };

  const removeFile = (fileName) => {
    setSelectedFiles((prev) => prev.filter((f) => f.name !== fileName));
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      addFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files.length > 0) {
      addFiles(Array.from(e.target.files));
    }
  };

  const handleSubmit = () => {
    if (selectedFiles.length > 0) {
      onUploadFiles(selectedFiles);
    }
  };

  return (
    <div style={{ padding: '3rem 0', textAlign: 'center' }}>
      {/* Hero Header */}
      <div style={{ marginBottom: '3rem' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(16, 185, 129, 0.1)', padding: '0.4rem 1rem', borderRadius: '50px', border: '1px solid rgba(16, 185, 129, 0.3)', marginBottom: '1.5rem' }}>
          <Activity size={16} color="#10b981" />
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#34d399', letterSpacing: '0.05em' }}>AI FRONTIER HEALTHCARE AUDITOR</span>
        </div>
        <h1 style={{ fontSize: '3.5rem', fontWeight: 800, marginBottom: '1rem', lineHeight: 1.1 }}>
          Stop Claim Rejections <br />
          <span className="gradient-text">Before Payer Submission.</span>
        </h1>
        <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', maxWidth: '650px', margin: '0 auto', lineHeight: 1.6 }}>
          ClaimIQ automatically classifies hospital packets, extracts clinical entities, cross-checks medical logic against billing items, and quantifies financial risk in seconds.
        </p>
      </div>

      {/* Stats Bar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', maxWidth: '800px', margin: '0 auto 3rem auto' }}>
        <div className="glass-card" style={{ padding: '1.2rem' }}>
          <h3 style={{ fontSize: '1.8rem', color: '#34d399', fontWeight: 700 }}>0%</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Human Oversight Error</p>
        </div>
        <div className="glass-card" style={{ padding: '1.2rem' }}>
          <h3 style={{ fontSize: '1.8rem', color: '#60a5fa', fontWeight: 700 }}>20x Faster</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Than Manual TPA Audit</p>
        </div>
        <div className="glass-card" style={{ padding: '1.2rem' }}>
          <h3 style={{ fontSize: '1.8rem', color: '#f59e0b', fontWeight: 700 }}>100%</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Deterministic Matching</p>
        </div>
      </div>

      {/* Main Upload Dropzone */}
      <div className="glass-card" style={{ maxWidth: '800px', margin: '0 auto', padding: '2.5rem', border: dragActive ? '2px dashed #10b981' : '1px solid var(--border-color)' }}
        onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}>
        
        <UploadCloud size={56} color={dragActive ? "#10b981" : "#64748b"} style={{ margin: '0 auto 1.5rem auto' }} />
        <h3 style={{ fontSize: '1.4rem', marginBottom: '0.5rem' }}>Drag & Drop Healthcare Claim PDFs Here</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginBottom: '2rem' }}>
          Upload Bills, Discharge Summaries, Prescriptions, Lab Reports, or TPA Claim Forms
        </p>

        <input type="file" id="file-upload" multiple accept=".pdf" onChange={handleChange} style={{ display: 'none' }} />
        <label htmlFor="file-upload" className="btn" style={{ background: 'rgba(255,255,255,0.08)', color: 'white', border: '1px solid rgba(255,255,255,0.15)', marginRight: '1rem' }}>
          Browse Files
        </label>

        {selectedFiles.length > 0 && (
          <div style={{ marginTop: '1.5rem', textAlign: 'left', background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '12px' }}>
            <p style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.5rem', color: '#34d399' }}>Selected ({selectedFiles.length} files):</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {selectedFiles.map((f, idx) => (
                <span key={idx} style={{ background: 'rgba(255,255,255,0.05)', padding: '0.3rem 0.6rem', borderRadius: '6px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.4rem', border: '1px solid rgba(255,255,255,0.1)' }}>
                  <FileText size={14} color="#60a5fa" /> 
                  <span>{f.name}</span>
                  <X size={14} color="#ef4444" style={{ cursor: 'pointer', marginLeft: '0.2rem' }} onClick={() => removeFile(f.name)} />
                </span>
              ))}
            </div>
            <button className="btn btn-primary" onClick={handleSubmit} disabled={isUploading} style={{ width: '100%', marginTop: '1rem' }}>
              {isUploading ? "Uploading..." : "Run AI Audit on Selected Files"} <ArrowRight size={18} />
            </button>
          </div>
        )}

        <div style={{ margin: '2rem 0', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ height: '1px', flex: 1, background: 'var(--border-color)' }} />
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Or For Live Pitching</span>
          <div style={{ height: '1px', flex: 1, background: 'var(--border-color)' }} />
        </div>

        {/* Demo Button */}
        <button className="btn btn-demo" onClick={onStartDemo} disabled={isUploading} style={{ width: '100%', padding: '1rem', fontSize: '1.1rem' }}>
          <Zap size={20} /> ⚡ Load Demo Claim Packet (6 Hospital Files with Planted Bugs)
        </button>
      </div>
    </div>
  );
}
