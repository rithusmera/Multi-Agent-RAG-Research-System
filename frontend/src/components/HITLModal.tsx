import React from 'react';
import { AlertTriangle, CheckCircle2, RefreshCw, XCircle } from 'lucide-react';

interface HITLModalProps {
  isOpen: boolean;
  onClose: () => void;
  onApprove: () => void;
  onRefine: (newPrompt: string) => void;
  evaluatorFeedback?: string;
  confidenceScore?: number;
}

export const HITLModal: React.FC<HITLModalProps> = ({
  isOpen,
  onClose,
  onApprove,
  onRefine,
  evaluatorFeedback = 'Evaluator Agent detected incomplete web research regarding real-time agent execution latency benchmarks.',
  confidenceScore = 0.68,
}) => {
  const [customPrompt, setCustomPrompt] = React.useState('');

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(6px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 100,
        padding: '20px',
      }}
    >
      <div
        style={{
          background: '#111827',
          border: '1px solid rgba(244, 63, 94, 0.4)',
          borderRadius: '16px',
          maxWidth: '540px',
          width: '100%',
          padding: '24px',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <div
            style={{
              padding: '10px',
              borderRadius: '50%',
              background: 'rgba(244, 63, 94, 0.15)',
              color: '#F43F5E',
              display: 'flex',
            }}
          >
            <AlertTriangle style={{ width: '22px', height: '22px' }} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#F9FAFB' }}>
              Human-in-the-Loop (HITL) Checkpoint
            </h3>
            <span style={{ fontSize: '12px', color: '#9CA3AF' }}>Evaluator Feedback Required</span>
          </div>
        </div>

        {/* Feedback Alert */}
        <div
          style={{
            background: '#161F2E',
            border: '1px solid #1F2937',
            borderRadius: '10px',
            padding: '14px',
            marginBottom: '16px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: 600, color: '#F43F5E' }}>EVALUATOR REASONING</span>
            <span style={{ fontSize: '11px', color: '#9CA3AF' }}>Confidence: {(confidenceScore * 100).toFixed(0)}%</span>
          </div>
          <p style={{ margin: 0, fontSize: '13px', color: '#E5E7EB', lineHeight: '1.5' }}>
            {evaluatorFeedback}
          </p>
        </div>

        {/* User Refinement Input */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#9CA3AF', marginBottom: '6px' }}>
            ADDITIONAL RESEARCH INSTRUCTIONS (OPTIONAL)
          </label>
          <textarea
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            placeholder="e.g. Focus specifically on recent 2026 benchmark data from HuggingFace..."
            rows={3}
            style={{
              width: '100%',
              boxSizing: 'border-box',
              background: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              padding: '10px 12px',
              color: '#F9FAFB',
              fontSize: '13px',
              outline: 'none',
              resize: 'vertical',
            }}
          />
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: '1px solid #374151',
              color: '#9CA3AF',
              padding: '8px 14px',
              borderRadius: '8px',
              fontSize: '13px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <XCircle style={{ width: '14px', height: '14px' }} /> Cancel
          </button>

          <button
            onClick={() => onRefine(customPrompt)}
            style={{
              background: 'rgba(245, 158, 11, 0.15)',
              border: '1px solid rgba(245, 158, 11, 0.4)',
              color: '#F59E0B',
              padding: '8px 14px',
              borderRadius: '8px',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <RefreshCw style={{ width: '14px', height: '14px' }} /> Re-evaluate Loop
          </button>

          <button
            onClick={onApprove}
            style={{
              background: '#10B981',
              border: 'none',
              color: '#0B0F17',
              padding: '8px 16px',
              borderRadius: '8px',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <CheckCircle2 style={{ width: '14px', height: '14px' }} /> Approve & Continue
          </button>
        </div>
      </div>
    </div>
  );
};
