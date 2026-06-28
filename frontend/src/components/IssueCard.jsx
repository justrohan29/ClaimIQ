import React from 'react';
import { AlertCircle, AlertTriangle, Info, ShieldAlert, CheckCircle, Wrench } from 'lucide-react';

export default function IssueCard({ issue }) {
  const sev = issue.severity || "info";
  
  let borderColor = "rgba(59, 130, 246, 0.4)";
  let badgeClass = "badge-blue";
  let Icon = Info;

  if (sev === "critical") {
    borderColor = "rgba(239, 68, 68, 0.6)";
    badgeClass = "badge-red";
    Icon = ShieldAlert;
  } else if (sev === "warning") {
    borderColor = "rgba(245, 158, 11, 0.6)";
    badgeClass = "badge-yellow";
    Icon = AlertTriangle;
  }

  return (
    <div className="glass-card" style={{ borderLeft: `5px solid ${sev === 'critical' ? '#ef4444' : sev === 'warning' ? '#f59e0b' : '#3b82f6'}`, marginBottom: '1.2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
          <span className={`badge ${badgeClass}`}>
            <Icon size={14} /> {sev.toUpperCase()}
          </span>
          <span style={{ fontSize: '0.85rem', color: '#94a3b8', fontWeight: 600 }}>
            Category: {issue.category || "General"}
          </span>
        </div>

        {issue.needs_human_review && (
          <span className="badge badge-yellow animate-pulse" style={{ background: 'rgba(245, 158, 11, 0.25)', borderColor: '#f59e0b' }}>
            ⚠️ HITL Escalation: Needs Human Review
          </span>
        )}
      </div>

      <h3 style={{ fontSize: '1.3rem', marginBottom: '0.6rem', color: '#f8fafc' }}>{issue.title}</h3>
      
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '1.2rem', lineHeight: 1.6 }}>
        {issue.explanation}
      </p>

      {/* Involved documents tag */}
      {issue.documents && issue.documents.length > 0 && (
        <div style={{ marginBottom: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Documents Involved:</span>
          {issue.documents.map((d, idx) => (
            <span key={idx} style={{ background: 'rgba(255,255,255,0.06)', padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.8rem', color: '#e2e8f0' }}>
              📄 {d}
            </span>
          ))}
        </div>
      )}

      {/* Actionable Fix Recommendation */}
      <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '1rem', borderRadius: '10px', display: 'flex', alignItems: 'flex-start', gap: '0.8rem' }}>
        <Wrench color="#34d399" size={20} style={{ marginTop: '0.1rem', flexShrink: 0 }} />
        <div>
          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#34d399', display: 'block', marginBottom: '0.2rem' }}>
            RECOMMENDED REMEDIATION STEP:
          </span>
          <span style={{ fontSize: '0.9rem', color: '#e2e8f0' }}>{issue.fix_recommendation}</span>
        </div>
      </div>
    </div>
  );
}
