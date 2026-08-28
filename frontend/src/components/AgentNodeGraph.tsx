import React from 'react';
import type { AgentRole } from './AgentBadge';

export interface NodeState {
  id: string;
  label: string;
  role: AgentRole;
  status: 'idle' | 'active' | 'completed' | 'paused';
  x: number;
  y: number;
}

interface AgentNodeGraphProps {
  activeNodeId?: string;
  onSelectNode?: (nodeId: string) => void;
}

const defaultNodes: NodeState[] = [
  { id: 'supervisor', label: 'Supervisor', role: 'supervisor', status: 'completed', x: 180, y: 50 },
  { id: 'rag', label: 'RAG Agent', role: 'rag', status: 'completed', x: 90, y: 140 },
  { id: 'research', label: 'Research Agent', role: 'research', status: 'active', x: 270, y: 140 },
  { id: 'evaluator', label: 'Evaluator', role: 'evaluator', status: 'idle', x: 180, y: 230 },
  { id: 'hitl', label: 'HITL Review', role: 'hitl', status: 'idle', x: 90, y: 310 },
  { id: 'response', label: 'Response Agent', role: 'response', status: 'idle', x: 270, y: 310 },
];

const connections = [
  { from: 'supervisor', to: 'rag' },
  { from: 'supervisor', to: 'research' },
  { from: 'rag', to: 'evaluator' },
  { from: 'research', to: 'evaluator' },
  { from: 'evaluator', to: 'hitl' },
  { from: 'evaluator', to: 'response' },
  { from: 'hitl', to: 'supervisor' },
];

const colorMap: Record<AgentRole, string> = {
  supervisor: '#F59E0B',
  research: '#10B981',
  rag: '#06B6D4',
  evaluator: '#8B5CF6',
  response: '#6366F1',
  hitl: '#F43F5E',
};

export const AgentNodeGraph: React.FC<AgentNodeGraphProps> = ({ activeNodeId = 'research', onSelectNode }) => {
  return (
    <div style={{ background: '#111827', borderRadius: '12px', border: '1px solid #1F2937', padding: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <span style={{ fontSize: '12px', fontWeight: 600, color: '#9CA3AF', letterSpacing: '0.05em' }}>
          LANGGRAPH EXECUTION CANVAS
        </span>
        <span style={{ fontSize: '11px', color: '#10B981', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10B981', display: 'inline-block' }} />
          LIVE PIPELINE
        </span>
      </div>

      <svg width="100%" height="360" viewBox="0 0 360 360" style={{ overflow: 'visible' }}>
        {connections.map((conn, idx) => {
          const source = defaultNodes.find((n) => n.id === conn.from);
          const target = defaultNodes.find((n) => n.id === conn.to);
          if (!source || !target) return null;

          const isHighlighted = source.id === activeNodeId || target.id === activeNodeId;

          return (
            <line
              key={idx}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              stroke={isHighlighted ? '#06B6D4' : '#374151'}
              strokeWidth={isHighlighted ? 2 : 1}
              strokeDasharray={isHighlighted ? '4,4' : 'none'}
              style={{ transition: 'all 0.3s ease' }}
            />
          );
        })}

        {defaultNodes.map((node) => {
          const isActive = node.id === activeNodeId;
          const strokeColor = colorMap[node.role];

          return (
            <g
              key={node.id}
              onClick={() => onSelectNode?.(node.id)}
              style={{ cursor: 'pointer', transition: 'all 0.3s ease' }}
            >
              {isActive && (
                <circle
                  cx={node.x}
                  cy={node.y}
                  r="24"
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth="2"
                  opacity="0.6"
                >
                  <animate attributeName="r" values="20;32;20" dur="2s" repeatCount="indefinite" />
                  <animate attributeName="opacity" values="0.8;0;0.8" dur="2s" repeatCount="indefinite" />
                </circle>
              )}

              <circle
                cx={node.x}
                cy={node.y}
                r="18"
                fill="#1F2937"
                stroke={strokeColor}
                strokeWidth={isActive ? 3 : 2}
              />

              <circle
                cx={node.x}
                cy={node.y}
                r="6"
                fill={isActive ? strokeColor : node.status === 'completed' ? '#10B981' : '#6B7280'}
              />

              <text
                x={node.x}
                y={node.y + 32}
                textAnchor="middle"
                fill={isActive ? '#F9FAFB' : '#9CA3AF'}
                fontSize="11"
                fontWeight={isActive ? '600' : '400'}
              >
                {node.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};
