import React from 'react';
import { DollarSign, AlertCircle, TrendingDown } from 'lucide-react';

export default function FinancialBanner({ financialData }) {
  const total = financialData?.total_claim_amount || 0.0;
  const atRisk = financialData?.amount_at_risk || 0.0;
  const hasFigures = total > 0;

  return (
    <div style={{
      background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(18, 27, 43, 0.8) 100%)',
      border: '1px solid rgba(239, 68, 68, 0.4)',
      borderRadius: '16px',
      padding: '1.5rem 2rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      boxShadow: '0 10px 30px -10px rgba(239, 68, 68, 0.2)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
        <div style={{ background: 'rgba(239, 68, 68, 0.2)', padding: '1rem', borderRadius: '12px', border: '1px solid rgba(239, 68, 68, 0.4)' }}>
          <TrendingDown color="#f87171" size={32} />
        </div>
        <div>
          <span className="badge badge-red" style={{ marginBottom: '0.5rem' }}>
            <AlertCircle size={14} /> Financial Risk Exposure
          </span>
          <h3 style={{ fontSize: '1.8rem', color: '#f8fafc', fontWeight: 700 }}>
            INR {atRisk.toLocaleString('en-IN', { minimumFractionDigits: 2 })} <span style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', fontWeight: 400 }}>at risk of deduction / rejection</span>
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            {hasFigures ? `Total Submitted Claim: INR ${total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : "Total Submitted Claim: N/A (No Billing Figures Detected in Uploaded PDFs)"}
          </p>
        </div>
      </div>

      <div style={{ textAlign: 'right' }}>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Risk Percentage</div>
        <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#f87171' }}>
          {hasFigures ? `${round((atRisk / total) * 100)}%` : "N/A"}
        </div>
      </div>
    </div>
  );
}

function round(val) {
  return Math.min(100, Math.round(val || 0));
}
