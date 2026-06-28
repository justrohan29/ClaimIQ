import React from 'react';
import { FileText, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

export default function DocumentInventory({ classifiedDocs, issues }) {
  if (!classifiedDocs) return null;

  return (
    <div style={{ marginTop: '3rem' }}>
      <h3 style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>📄 Digitized Claim Document Inventory</h3>
      <div className="grid-3">
        {Object.entries(classifiedDocs).map(([filename, doc]) => {
          const dtype = doc.doc_type || "unknown";
          const title = dtype.replace("_", " ").toUpperCase();
          const conf = doc.confidence || 0.95;
          
          // Check if document has issues associated with it
          const docIssues = issues.filter(i => i.documents.some(d => d.toLowerCase().replace(" ", "_") === dtype));
          const hasCritical = docIssues.some(i => i.severity === "critical");
          const hasWarning = docIssues.some(i => i.severity === "warning");

          let statusIcon = <CheckCircle2 color="#10b981" size={20} />;
          let statusText = "Clean";
          let badgeClass = "badge-green";

          if (hasCritical) {
            statusIcon = <XCircle color="#ef4444" size={20} />;
            statusText = "Discrepancy Flagged";
            badgeClass = "badge-red";
          } else if (hasWarning) {
            statusIcon = <AlertTriangle color="#f59e0b" size={20} />;
            statusText = "Review Needed";
            badgeClass = "badge-yellow";
          }

          return (
            <div key={filename} className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <span style={{ fontSize: '0.8rem', color: '#60a5fa', fontWeight: 600, background: 'rgba(59, 130, 246, 0.1)', padding: '0.25rem 0.6rem', borderRadius: '6px' }}>
                    {title}
                  </span>
                  <span className={`badge ${badgeClass}`}>
                    {statusIcon} {statusText}
                  </span>
                </div>

                <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', wordBreak: 'break-all' }}>{filename}</h4>
                
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '1rem', borderTop: '1px solid var(--border-color)', paddingTop: '0.8rem' }}>
                  {doc.patient_name && <div><strong>Patient:</strong> {doc.patient_name}</div>}
                  {doc.admission_date && <div><strong>Adm Date:</strong> {doc.admission_date}</div>}
                  {doc.total_amount && <div><strong>Amount:</strong> INR {floatFormat(doc.total_amount)}</div>}
                  {doc.doctor_name && <div><strong>Doctor:</strong> {doc.doctor_name}</div>}
                </div>
              </div>

              <div style={{ marginTop: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                <span>OCR Confidence:</span>
                <span style={{ color: '#34d399', fontWeight: 600 }}>{Math.round(conf * 100)}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function floatFormat(val) {
  try {
    return Number(val).toLocaleString('en-IN');
  } catch {
    return String(val);
  }
}
