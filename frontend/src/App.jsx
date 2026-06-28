import React, { useState } from 'react';
import UploadZone from './components/UploadZone';
import PipelineProgress from './components/PipelineProgress';
import ScoreGauge from './components/ScoreGauge';
import FinancialBanner from './components/FinancialBanner';
import DocumentInventory from './components/DocumentInventory';
import IssueCard from './components/IssueCard';
import ClaimTimeline from './components/ClaimTimeline';
import { Sparkles, RefreshCw, CheckCircle2, ArrowRight } from 'lucide-react';

const API_BASE = "http://localhost:8000";

export default function App() {
  const [appState, setAppState] = useState('upload'); // 'upload' | 'processing' | 'dashboard'
  const [isUploading, setIsUploading] = useState(false);
  
  // Pipeline streaming state
  const [currentStage, setCurrentStage] = useState(1);
  const [progress, setProgress] = useState(5);
  const [statusMessage, setStatusMessage] = useState("Initializing AI agents...");
  
  // Final Audit Result
  const [auditData, setAuditData] = useState(null);

  const startStreaming = (claimId) => {
    setAppState('processing');
    setCurrentStage(1);
    setProgress(10);
    setStatusMessage("Connecting to ClaimIQ SSE processing stream...");

    const es = new EventSource(`${API_BASE}/api/stream/${claimId}`);
    
    es.addEventListener('progress', (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.stage) setCurrentStage(data.stage);
        if (data.progress) setProgress(data.progress);
        if (data.message) setStatusMessage(data.message);
      } catch (err) {
        console.error("Error parsing progress SSE:", err);
      }
    });

    es.addEventListener('complete', (e) => {
      try {
        const payload = JSON.parse(e.data);
        setAuditData(payload);
        setProgress(100);
        setCurrentStage(6);
        setTimeout(() => {
          setAppState('dashboard');
          es.close();
        }, 800);
      } catch (err) {
        console.error("Error parsing complete SSE:", err);
      }
    });

    es.onerror = (err) => {
      console.error("SSE Error:", err);
      setStatusMessage("Connection error or audit complete.");
      es.close();
    };
  };

  const handleStartDemo = async () => {
    setIsUploading(true);
    try {
      const res = await fetch(`${API_BASE}/api/prepare-demo`, { method: 'POST' });
      const data = await res.json();
      if (data.claim_id) {
        startStreaming(data.claim_id);
      } else {
        alert("Error loading demo data: " + (data.error || "Unknown"));
      }
    } catch (err) {
      alert("Failed to connect to FastAPI server at " + API_BASE + ". Make sure backend is running!");
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleUploadFiles = async (files) => {
    setIsUploading(true);
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));

    try {
      const res = await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.claim_id) {
        startStreaming(data.claim_id);
      } else {
        alert("Upload error.");
      }
    } catch (err) {
      alert("Failed to upload files to backend.");
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleReset = () => {
    setAppState('upload');
    setAuditData(null);
  };

  return (
    <div className="app-container">
      {/* Top Navbar */}
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', cursor: 'pointer' }} onClick={handleReset}>
          <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'linear-gradient(135deg, #10b981, #3b82f6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '1.2rem', color: 'white' }}>
            Q
          </div>
          <span style={{ fontSize: '1.4rem', fontWeight: 800, fontFamily: 'var(--font-heading)' }}>Claim<span style={{ color: '#34d399' }}>IQ</span></span>
        </div>

        {appState === 'dashboard' && (
          <button className="btn" onClick={handleReset} style={{ background: 'rgba(255,255,255,0.08)', color: 'white', border: '1px solid rgba(255,255,255,0.15)' }}>
            <RefreshCw size={16} /> Audit Another Claim
          </button>
        )}
      </header>

      {/* Main Views */}
      {appState === 'upload' && (
        <UploadZone onStartDemo={handleStartDemo} onUploadFiles={handleUploadFiles} isUploading={isUploading} />
      )}

      {appState === 'processing' && (
        <PipelineProgress currentStage={currentStage} progress={progress} statusMessage={statusMessage} />
      )}

      {appState === 'dashboard' && auditData && (
        <div>
          {/* Top Gauge & Financial Banner */}
          <div className="grid-2" style={{ marginBottom: '2rem' }}>
            <ScoreGauge scoreData={auditData.score} />
            <FinancialBanner financialData={auditData.score?.financial_impact} />
          </div>

          {/* Claims Intelligence Executive Summary */}
          <div className="glass-card" style={{ marginBottom: '3rem', border: '1px solid rgba(16, 185, 129, 0.3)', background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(18, 27, 43, 0.8) 100%)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
              <Sparkles color="#34d399" size={22} />
              <h3 style={{ fontSize: '1.4rem', color: '#34d399' }}>Claims Intelligence Executive Briefing</h3>
            </div>
            <p style={{ fontSize: '1.1rem', color: '#f8fafc', lineHeight: 1.7, fontStyle: 'italic' }}>
              "{auditData.report?.summary}"
            </p>
          </div>

          {/* Timeline */}
          <ClaimTimeline timelineEvents={auditData.report?.timeline || []} />

          {/* Issues Found */}
          <div style={{ marginTop: '3rem', marginBottom: '3rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.5rem' }}>⚠️ Detected Discrepancies & Audit Failures ({auditData.issues?.length || 0})</h3>
              <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Sorted by priority & severity</span>
            </div>

            {auditData.issues?.length === 0 ? (
              <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', color: '#34d399' }}>
                <CheckCircle2 size={48} style={{ margin: '0 auto 1rem auto' }} />
                <h3>No Discrepancies Found! This claim packet is clean and ready for immediate TPA submission.</h3>
              </div>
            ) : (
              auditData.issues?.map((iss, idx) => (
                <IssueCard key={idx} issue={iss} />
              ))
            )}
          </div>

          {/* Prioritized Fixes Checklist */}
          {auditData.report?.fixes && auditData.report.fixes.length > 0 && (
            <div className="glass-card" style={{ padding: '2rem', marginBottom: '3rem' }}>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '1.5rem', color: '#60a5fa' }}>🎯 Prioritized Remediation Roadmap</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {auditData.report.fixes.map((fx, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(255,255,255,0.03)', padding: '1rem 1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <span style={{ width: '28px', height: '28px', borderRadius: '50%', background: '#3b82f6', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.9rem' }}>
                        {fx.priority || idx + 1}
                      </span>
                      <span style={{ fontSize: '1.05rem', fontWeight: 500 }}>{fx.action}</span>
                    </div>
                    <span className="badge badge-green" style={{ fontSize: '0.85rem' }}>
                      Gain {fx.expected_score_gain}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Document Inventory Grid */}
          <DocumentInventory classifiedDocs={auditData.classified_documents} issues={auditData.issues || []} />
        </div>
      )}
    </div>
  );
}
