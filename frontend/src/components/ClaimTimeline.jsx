import React from 'react';
import { Calendar, AlertCircle, CheckCircle } from 'lucide-react';

export default function ClaimTimeline({ timelineEvents }) {
  const events = timelineEvents || [];

  if (events.length === 0) {
    return (
      <div style={{ marginTop: '3rem', marginBottom: '3rem' }}>
        <h3 style={{ fontSize: '1.5rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Calendar color="#60a5fa" /> Hospitalization & Clinical Timeline
        </h3>
        <div className="glass-card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          No chronological dates detected across the submitted documents.
        </div>
      </div>
    );
  }

  return (
    <div style={{ marginTop: '3rem', marginBottom: '3rem' }}>
      <h3 style={{ fontSize: '1.5rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
        <Calendar color="#60a5fa" /> Hospitalization & Clinical Timeline
      </h3>

      <div className="glass-card" style={{ padding: '2rem' }}>
        <div style={{ position: 'relative', paddingLeft: '2rem', borderLeft: '2px solid rgba(255,255,255,0.15)' }}>
          {events.map((ev, idx) => (
            <div key={idx} style={{ position: 'relative', marginBottom: idx === events.length - 1 ? 0 : '2rem' }}>
              {/* Timeline circle dot */}
              <div style={{
                position: 'absolute',
                left: '-2.55rem',
                top: '0.2rem',
                width: '16px',
                height: '16px',
                borderRadius: '50%',
                background: ev.flag ? '#ef4444' : '#10b981',
                border: '3px solid #0a0f18'
              }} />

              <div style={{ display: 'flex', alignItems: 'baseline', gap: '1rem', marginBottom: '0.3rem', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>{ev.date || "Unknown Date"}</span>
                {ev.doc && (
                  <span style={{ fontSize: '0.8rem', background: 'rgba(255,255,255,0.08)', padding: '0.2rem 0.6rem', borderRadius: '4px', color: '#94a3b8' }}>
                    📄 {ev.doc}
                  </span>
                )}
              </div>

              <p style={{ fontSize: '1rem', color: '#e2e8f0', marginBottom: ev.flag ? '0.5rem' : 0 }}>{ev.label || "Clinical Event"}</p>

              {ev.flag && (
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '0.3rem 0.8rem', borderRadius: '6px', fontSize: '0.85rem', color: '#f87171', marginTop: '0.4rem' }}>
                  <AlertCircle size={14} /> {ev.flag}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
