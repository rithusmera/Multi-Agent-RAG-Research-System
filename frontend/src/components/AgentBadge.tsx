import React from 'react';
import { Compass, Globe, Database, CheckCircle2, MessageSquare, AlertTriangle } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export type AgentRole = 'supervisor' | 'research' | 'rag' | 'evaluator' | 'response' | 'hitl';

interface AgentBadgeProps {
  role: AgentRole;
  label?: string;
  size?: 'sm' | 'md';
}

const roleConfigs: Record<AgentRole, { name: string; color: string; bg: string; border: string; icon: LucideIcon }> = {
  supervisor: {
    name: 'Supervisor Router',
    color: '#F59E0B',
    bg: 'rgba(245, 158, 11, 0.12)',
    border: 'rgba(245, 158, 11, 0.3)',
    icon: Compass,
  },
  research: {
    name: 'Research Agent',
    color: '#10B981',
    bg: 'rgba(16, 185, 129, 0.12)',
    border: 'rgba(16, 185, 129, 0.3)',
    icon: Globe,
  },
  rag: {
    name: 'RAG Agent',
    color: '#06B6D4',
    bg: 'rgba(6, 182, 212, 0.12)',
    border: 'rgba(6, 182, 212, 0.3)',
    icon: Database,
  },
  evaluator: {
    name: 'Evaluator Agent',
    color: '#8B5CF6',
    bg: 'rgba(139, 92, 246, 0.12)',
    border: 'rgba(139, 92, 246, 0.3)',
    icon: CheckCircle2,
  },
  response: {
    name: 'Response Agent',
    color: '#6366F1',
    bg: 'rgba(99, 102, 241, 0.12)',
    border: 'rgba(99, 102, 241, 0.3)',
    icon: MessageSquare,
  },
  hitl: {
    name: 'Human Checkpoint',
    color: '#F43F5E',
    bg: 'rgba(244, 63, 94, 0.15)',
    border: 'rgba(244, 63, 94, 0.4)',
    icon: AlertTriangle,
  },
};

export const AgentBadge: React.FC<AgentBadgeProps> = ({ role, label, size = 'md' }) => {
  const config = roleConfigs[role] || roleConfigs.supervisor;
  const Icon = config.icon;

  const isSmall = size === 'sm';

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: isSmall ? '2px 8px' : '4px 10px',
        borderRadius: '9999px',
        backgroundColor: config.bg,
        border: `1px solid ${config.border}`,
        color: config.color,
        fontSize: isSmall ? '11px' : '12px',
        fontWeight: 600,
        letterSpacing: '0.03em',
        textTransform: 'uppercase',
      }}
    >
      <Icon style={{ width: isSmall ? '12px' : '14px', height: isSmall ? '12px' : '14px' }} />
      {label || config.name}
    </span>
  );
};
