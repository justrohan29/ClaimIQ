import React from 'react';
import { CheckCircle2, Loader2, Circle, Activity, ShieldAlert } from 'lucide-react';

const STAGES = [
  { id: 1, title: "Document Digitization", desc: "Extracting text and structure via Docling OCR" },
  { id: 2, title: "AI Document Classification", desc: "Identifying claim form, bills, and clinical reports" },
  { id: 3, title: "Clinical Deep Extraction", desc: "Parsing itemized charges, medications & ICD codes" },
  { id: 4, title: "Consistency & Medical Verification", desc: "Cross-checking dates, identity & clinical logic" },
  { id: 5, title: "Claims Intelligence & Scoring", desc: "Calculating readiness gauge and financial exposure" },
  { id: 6, title: "Audit Complete", desc: "Generating final executive briefing" }
];

export default function PipelineProgress({ currentStage, progress, statusMessage }) {
  return (
    <div style={{ maxWidth: '800px', margin: '4rem auto', padding: '1rem' }}>
      <div className="glass-card" style={{ padding: '2.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
          <div>
            <h2 style={{ fontSize: '1.8rem', marginBottom: '0.3rem' }}>AI Multi-Agent Audit Pipeline</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>Real-time deep cognitive analysis in progress...</p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '2rem', fontWeight: 800, color: '#34d399' }}>{progress}%</span>
          </div>
        </div>

        {/* Progress bar */}
        <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.08)', borderRadius: '4px', overflow: 'hidden', marginBottom: '3rem' }}>
          <div style={{ width: `${progress}%`, height: '100%', background: 'linear-gradient(90deg, #3b82f6, #10b981)', transition: 'width 0.5s ease' }} />
        </div>

        {/* Live status banner */}
        {statusMessage && (
          <div style={{ background: 'rgba(59, 130, 246, 0.1)', borderLeft: '4px solid #3b82f6', padding: '1rem 1.5rem', borderRadius: '8px', marginBottom: '3rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <Activity className="animate-pulse" color="#60a5fa" size={24} />
            <span style={{ fontSize: '1rem', color: '#f8fafc', fontWeight: 500 }}>{statusMessage}</span>
          </div>
        )}

        {/* Vertical Stages */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', position: 'relative' }}>
          {STAGES.map((stg) => {
            const isDone = currentStage > stg.id || currentStage === 6;
            const isRunning = currentStage === stg.id && currentStage !== 6;
            const isPending = currentStage < stg.id;

            return (
              <div key={stg.id} style={{ display: 'flex', alignItems: 'flex-start', gap: '1.2rem', opacity: isPending ? 0.4 : 1, transition: 'opacity 0.3s ease' }}>
                <div style={{ marginTop: '0.2rem' }}>
                  {isDone ? (
                    <CheckCircle2 color="#10b981" size={28} />
                  ) : isRunning ? (
                    <Loader2 className="spinner" color="#60a5fa" size={28} />
                  ) : (
                    <Circle color="#64748b" size={28} />
                  )}
                </div>
                <div style={{ flex: 1 }}>
                  <h4 style={{ fontSize: '1.15rem', color: isRunning ? '#60a5fa' : isDone ? '#f8fafc' : 'var(--text-secondary)', marginBottom: '0.2rem' }}>
                    {stg.title}
                  </h4>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{stg.desc}</p>
                </div>
                {isRunning && (
                  <span className="badge badge-blue animate-pulse">Running</span>
                )}
                {isDone && (
                  <span className="badge badge-green">Complete</span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
