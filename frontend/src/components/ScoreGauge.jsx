import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle } from 'lucide-react';

export default function ScoreGauge({ scoreData }) {
  const score = scoreData?.overall_score || 0;
  const risk = scoreData?.risk_level || "Unknown";

  let color = "#10b981"; // green
  let badgeClass = "badge-green";
  let Icon = ShieldCheck;

  if (score < 60) {
    color = "#ef4444"; // red
    badgeClass = "badge-red";
    Icon = ShieldAlert;
  } else if (score < 80) {
    color = "#f59e0b"; // yellow
    badgeClass = "badge-yellow";
    Icon = AlertTriangle;
  }

  // Circular progress math
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="glass-card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '2rem' }}>
      <div style={{ flex: 1 }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <span className={`badge ${badgeClass}`} style={{ fontSize: '0.9rem', padding: '0.4rem 1rem' }}>
            <Icon size={16} /> {risk} Risk Claim Packet
          </span>
        </div>
        <h2 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>Readiness Score</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1rem', maxWidth: '400px' }}>
          Calculated based on document completeness, identity verification, timeline integrity, financial math, and clinical logic.
        </p>
      </div>

      <div style={{ position: 'relative', width: '180px', height: '180px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <svg width="180" height="180" style={{ transform: 'rotate(-90deg)' }}>
          {/* Background circle */}
          <circle cx="90" cy="90" r={radius} stroke="rgba(255,255,255,0.08)" strokeWidth="14" fill="transparent" />
          {/* Progress circle */}
          <circle
            cx="90" cy="90" r={radius}
            stroke={color} strokeWidth="14"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            style={{ transition: 'stroke-dashoffset 1s ease-out' }}
          />
        </svg>
        <div style={{ position: 'absolute', textAlign: 'center' }}>
          <span style={{ fontSize: '2.8rem', fontWeight: 800, color: color, lineHeight: 1 }}>{score}</span>
          <span style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>/100</span>
        </div>
      </div>
    </div>
  );
}
