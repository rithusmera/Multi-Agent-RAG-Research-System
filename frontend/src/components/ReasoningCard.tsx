import React, { useState } from 'react';
import { AgentBadge } from './AgentBadge';
import type { AgentRole } from './AgentBadge';
import { ChevronDown, ChevronRight, ExternalLink, FileText, Sparkles } from 'lucide-react';

interface ReasoningCardProps {
  role: AgentRole;
  stepNumber: number;
  title: string;
  thought: string;
  sources?: Array<{ title: string; url?: string; type: 'web' | 'kb'; score?: number }>;
  executionTimeMs?: number;
  isStreaming?: boolean;
}

export const ReasoningCard: React.FC<ReasoningCardProps> = ({
  role,
  stepNumber,
  title,
  thought,
  sources = [],
  executionTimeMs = 420,
  isStreaming = false,
}) => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div
      style={{
        background: '#111827',
        border: '1px solid #1F2937',
        borderRadius: '10px',
        marginBottom: '12px',
        overflow: 'hidden',
      }}
    >
      <div
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 16px',
          background: '#161F2E',
          cursor: 'pointer',
          borderBottom: isOpen ? '1px solid #1F2937' : 'none',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '11px', color: '#6B7280', fontWeight: 600 }}>STEP {stepNumber}</span>
          <AgentBadge role={role} size="sm" />
          <span style={{ fontSize: '13px', fontWeight: 600, color: '#F9FAFB' }}>{title}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {isStreaming ? (
            <span style={{ fontSize: '11px', color: '#06B6D4', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Sparkles style={{ width: '12px', height: '12px' }} /> STREAMING
            </span>
          ) : (
            <span style={{ fontSize: '11px', color: '#6B7280' }}>{executionTimeMs}ms</span>
          )}
          {isOpen ? (
            <ChevronDown style={{ width: '16px', height: '16px', color: '#9CA3AF' }} />
          ) : (
            <ChevronRight style={{ width: '16px', height: '16px', color: '#9CA3AF' }} />
          )}
        </div>
      </div>

      {isOpen && (
        <div style={{ padding: '16px' }}>
          <p style={{ margin: 0, fontSize: '13px', color: '#D1D5DB', lineHeight: '1.6', whiteSpace: 'pre-line' }}>
            {thought}
          </p>

          {sources.length > 0 && (
            <div style={{ marginTop: '14px', paddingTop: '12px', borderTop: '1px solid #1F2937' }}>
              <div style={{ fontSize: '11px', fontWeight: 600, color: '#9CA3AF', marginBottom: '8px' }}>
                RETRIEVED SOURCES ({sources.length})
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {sources.map((src, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      background: '#1F2937',
                      padding: '6px 10px',
                      borderRadius: '6px',
                      fontSize: '12px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#E5E7EB' }}>
                      {src.type === 'web' ? (
                        <ExternalLink style={{ width: '12px', height: '12px', color: '#10B981' }} />
                      ) : (
                        <FileText style={{ width: '12px', height: '12px', color: '#06B6D4' }} />
                      )}
                      <span>{src.title}</span>
                    </div>
                    {src.score && (
                      <span style={{ fontSize: '10px', color: '#9CA3AF', background: '#111827', padding: '2px 6px', borderRadius: '4px' }}>
                        Score: {src.score}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
