import React, { useState, useEffect } from 'react';
import { AgentBadge } from './AgentBadge';
import { AgentNodeGraph } from './AgentNodeGraph';
import { HITLModal } from './HITLModal';
import {
  fetchKBDocuments,
  streamResearchQuery,
  approveHitlCheckpoint,
} from '../api/client';
import type { AgentStepEvent, KBDocument, HitlCheckpointEvent } from '../api/client';
import {
  Send,
  Plus,
  History,
  FileText,
  ShieldCheck,
  Layers,
  Search,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';

export const ResearchConsole: React.FC = () => {
  const [query, setQuery] = useState('');
  const [activeQuery, setActiveQuery] = useState(
    'Evaluate the performance differences between internal BM25 retrieval vs DuckDuckGo web search in a multi-agent RAG workflow.'
  );
  const [isHitlOpen, setIsHitlOpen] = useState(false);
  const [hitlData, setHitlData] = useState<HitlCheckpointEvent | null>(null);
  const [activeNode, setActiveNode] = useState('research');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentThreadId, setCurrentThreadId] = useState<string>('demo-thread-101');

  const [documents, setDocuments] = useState<KBDocument[]>([]);
  const [_steps, setSteps] = useState<AgentStepEvent[]>([
    {
      thread_id: 'demo-thread-101',
      step_index: 1,
      agent: 'supervisor',
      title: 'Route Query Intent',
      thought: 'Parsed user query. Initiating parallel execution paths: RAG Agent for internal PDF specs & Research Agent for live web search.',
      execution_time_ms: 180,
    },
    {
      thread_id: 'demo-thread-101',
      step_index: 2,
      agent: 'rag',
      title: 'Internal Knowledge Base Retrieval',
      thought: 'Executed BM25 keyword retrieval over internal index. Found 3 matches in multi_agent_rag_architecture.pdf with high relevancy scores.',
      sources: [
        { title: 'multi_agent_rag_architecture.pdf (Page 4)', type: 'kb', score: 0.92 },
        { title: 'bm25_retrieval_benchmarks.json', type: 'kb', score: 0.88 },
      ],
      execution_time_ms: 340,
    },
    {
      thread_id: 'demo-thread-101',
      step_index: 3,
      agent: 'research',
      title: 'DuckDuckGo Web Research',
      thought: 'Querying DuckDuckGo API for 2026 multi-agent RAG latency comparisons. Gathering external benchmark metrics...',
      sources: [
        { title: 'LangGraph Multi-Agent Architecture Guide', url: 'https://python.langchain.com', type: 'web' },
      ],
      execution_time_ms: 620,
    },
  ]);

  const [finalAnswer, setFinalAnswer] = useState<string | null>(
    `# Executive Summary
In multi-agent RAG workflows, combining internal BM25 keyword search with external web research optimizes retrieval latency and factual coverage.

# Key Findings
- **Internal BM25 Retrieval**: Delivers sub-50ms latency for indexed PDF/Markdown technical documentation with high exact-match precision (0.92 relevancy score).
- **DuckDuckGo Web Search**: Provides real-time external benchmarks and API specifications (300-600ms latency).
- **Evaluator Quality Feedback**: Re-routes insufficient context passes to fill missing topics before final answer synthesis.`
  );
  const [evalScore, setEvalScore] = useState<number>(84);
  const [executionError, setExecutionError] = useState<string | null>(null);

  // Fetch KB documents on mount
  useEffect(() => {
    fetchKBDocuments().then(setDocuments);
  }, []);

  const handleRunQuery = (searchQuery?: string, forceHitl: boolean = false) => {
    const q = searchQuery || query;
    if (!q.trim()) return;

    setActiveQuery(q);
    setIsStreaming(true);
    setFinalAnswer(null);
    setExecutionError(null);
    setSteps([]);
    setActiveNode('supervisor');

    const newThreadId = `thread-${Date.now().toString().slice(-6)}`;
    setCurrentThreadId(newThreadId);

    streamResearchQuery(q, {
      threadId: newThreadId,
      forceHitl,
      onStep: (event) => {
        setSteps((prev) => [...prev, event]);
        if (event.agent) {
          setActiveNode(event.agent);
        }
        if (event.evaluation?.score) {
          setEvalScore(event.evaluation.score);
        }
      },
      onHitl: (event) => {
        setIsStreaming(false);
        setHitlData(event);
        setIsHitlOpen(true);
        setActiveNode('hitl');
      },
      onFinalAnswer: (event) => {
        setIsStreaming(false);
        setFinalAnswer(event.final_answer);
        setActiveNode('response');
        if (event.evaluation?.score) {
          setEvalScore(event.evaluation.score);
        }
      },
      onError: (err) => {
        setIsStreaming(false);
        setExecutionError(err instanceof Error ? err.message : 'Research execution failed');
        console.error('Execution error:', err);
      },
    });
  };

  const handleApproveHitl = async (feedback?: string) => {
    setIsHitlOpen(false);
    setIsStreaming(true);

    try {
      const res = await approveHitlCheckpoint(currentThreadId, feedback);
      setIsStreaming(false);
      if (res.final_answer) {
        setFinalAnswer(res.final_answer);
        setActiveNode('response');
      }
    } catch (err) {
      setIsStreaming(false);
      console.error('Error approving HITL checkpoint:', err);
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', background: '#0B0F17', color: '#F9FAFB', overflow: 'hidden' }}>
      {/* 1. LEFT SIDEBAR (Navigation & KB Index) */}
      <div
        style={{
          width: '260px',
          background: '#111827',
          borderRight: '1px solid #1F2937',
          display: 'flex',
          flexDirection: 'column',
          flexShrink: 0,
        }}
      >
        <div style={{ padding: '16px', borderBottom: '1px solid #1F2937', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ background: '#06B6D4', color: '#0B0F17', padding: '6px', borderRadius: '8px', display: 'flex' }}>
            <Layers style={{ width: '18px', height: '18px' }} />
          </div>
          <div>
            <div style={{ fontSize: '14px', fontWeight: 700, letterSpacing: '0.02em' }}>Multi-Agent RAG</div>
            <div style={{ fontSize: '11px', color: '#9CA3AF' }}>Research Studio v2.4</div>
          </div>
        </div>

        <div style={{ padding: '12px 16px' }}>
          <button
            onClick={() => {
              setQuery('');
              setSteps([]);
              setFinalAnswer(null);
            }}
            style={{
              width: '100%',
              background: '#1F2937',
              border: '1px solid #374151',
              color: '#F9FAFB',
              padding: '8px 12px',
              borderRadius: '8px',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
            }}
          >
            <Plus style={{ width: '14px', height: '14px' }} /> New Research Query
          </button>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '0 16px' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: '#6B7280', letterSpacing: '0.05em', marginBottom: '8px' }}>
            INTERNAL KNOWLEDGE BASE
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginBottom: '20px' }}>
            {documents.map((doc) => (
              <div
                key={doc.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '6px 8px',
                  borderRadius: '6px',
                  fontSize: '12px',
                  color: '#D1D5DB',
                  background: 'transparent',
                  cursor: 'pointer',
                }}
              >
                <FileText style={{ width: '13px', height: '13px', color: '#06B6D4' }} />
                <span style={{ textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>{doc.name}</span>
              </div>
            ))}
          </div>

          <div style={{ fontSize: '11px', fontWeight: 600, color: '#6B7280', letterSpacing: '0.05em', marginBottom: '8px' }}>
            RECENT SESSIONS
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {[
              'LangGraph state persistence analysis',
              'BM25 vs Vector search latency',
              'Evaluator feedback loop design',
            ].map((session, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '6px 8px',
                  borderRadius: '6px',
                  fontSize: '12px',
                  color: '#9CA3AF',
                  cursor: 'pointer',
                }}
              >
                <History style={{ width: '13px', height: '13px' }} />
                <span style={{ textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>{session}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 2. CENTER CANVAS (Research Thread & Stream Output) */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', background: '#0B0F17' }}>
        {/* Top Header */}
        <div
          style={{
            height: '56px',
            borderBottom: '1px solid #1F2937',
            padding: '0 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: '#111827',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '14px', fontWeight: 600 }}>Autonomous Research Pipeline</span>
            {isStreaming ? (
              <span style={{ fontSize: '11px', color: '#06B6D4', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Sparkles style={{ width: '14px', height: '14px' }} /> Executing Agents...
              </span>
            ) : (
              <AgentBadge role="research" label="Pipeline Idle" size="sm" />
            )}
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => handleRunQuery(query || activeQuery, true)}
              style={{
                background: 'rgba(244, 63, 94, 0.15)',
                border: '1px solid rgba(244, 63, 94, 0.4)',
                color: '#F43F5E',
                padding: '4px 10px',
                borderRadius: '6px',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <ShieldCheck style={{ width: '14px', height: '14px' }} /> Test HITL Checkpoint
            </button>
          </div>
        </div>

        {/* Chat / Stream Thread */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px' }}>
          {/* User Input Prompt Card */}
          <div style={{ background: '#161F2E', border: '1px solid #1F2937', borderRadius: '10px', padding: '14px', marginBottom: '20px' }}>
            <div style={{ fontSize: '11px', color: '#9CA3AF', fontWeight: 600, marginBottom: '4px' }}>ACTIVE RESEARCH QUERY</div>
            <div style={{ fontSize: '14px', color: '#F9FAFB', fontWeight: 500 }}>
              "{activeQuery}"
            </div>
          </div>

          {executionError && (
            <div style={{ background: 'rgba(244, 63, 94, 0.08)', border: '1px solid rgba(244, 63, 94, 0.35)', borderRadius: '10px', padding: '14px', marginBottom: '20px', color: '#FDA4AF', fontSize: '13px' }}>
              Research execution failed: {executionError}
            </div>
          )}

          {/* Agent Answer / Streaming Status */}
          {finalAnswer ? (
            <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '12px', padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', color: '#10B981', fontWeight: 600, fontSize: '13px' }}>
                <CheckCircle2 style={{ width: '16px', height: '16px' }} /> Synthesized Final Answer
              </div>
              <div style={{ fontSize: '14px', color: '#F9FAFB', lineHeight: '1.7', whiteSpace: 'pre-line' }}>
                {finalAnswer}
              </div>
            </div>
          ) : isStreaming ? (
            <div style={{ background: '#161F2E', border: '1px solid #1F2937', borderRadius: '12px', padding: '20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Sparkles style={{ width: '18px', height: '18px', color: '#06B6D4' }} />
              <div>
                <div style={{ fontSize: '13px', fontWeight: 600, color: '#F9FAFB' }}>Generating Synthesized Research Answer...</div>
                <div style={{ fontSize: '11px', color: '#9CA3AF', marginTop: '2px' }}>Multi-agent workflow executing across Knowledge Base & Web Search. Follow node execution on the canvas.</div>
              </div>
            </div>
          ) : null}
        </div>

        {/* Input Bar */}
        <div style={{ padding: '16px 24px', borderTop: '1px solid #1F2937', background: '#111827' }}>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleRunQuery();
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              background: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '10px',
              padding: '6px 12px',
            }}
          >
            <Search style={{ width: '16px', height: '16px', color: '#9CA3AF', marginRight: '10px' }} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a deep-dive research topic or instruct agents..."
              style={{
                flex: 1,
                background: 'transparent',
                border: 'none',
                color: '#F9FAFB',
                fontSize: '13px',
                outline: 'none',
              }}
            />
            <button
              type="submit"
              disabled={isStreaming}
              style={{
                background: isStreaming ? '#374151' : '#06B6D4',
                border: 'none',
                color: isStreaming ? '#9CA3AF' : '#0B0F17',
                padding: '6px 12px',
                borderRadius: '6px',
                fontWeight: 600,
                cursor: isStreaming ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <Send style={{ width: '14px', height: '14px' }} /> Run
            </button>
          </form>
        </div>
      </div>

      {/* 3. RIGHT INSPECTOR (Node Graph & Telemetry) */}
      <div
        style={{
          width: '360px',
          background: '#111827',
          borderLeft: '1px solid #1F2937',
          display: 'flex',
          flexDirection: 'column',
          flexShrink: 0,
        }}
      >
        <div style={{ padding: '16px', borderBottom: '1px solid #1F2937' }}>
          <AgentNodeGraph activeNodeId={activeNode} onSelectNode={(id) => setActiveNode(id)} />
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: '#6B7280', letterSpacing: '0.05em', marginBottom: '10px' }}>
            EVALUATOR METRICS
          </div>

          <div style={{ background: '#161F2E', border: '1px solid #1F2937', borderRadius: '8px', padding: '12px', marginBottom: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '6px' }}>
              <span style={{ color: '#9CA3AF' }}>Information Sufficiency</span>
              <span style={{ color: '#10B981', fontWeight: 600 }}>{evalScore}%</span>
            </div>
            <div style={{ width: '100%', height: '6px', background: '#1F2937', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: `${evalScore}%`, height: '100%', background: '#10B981', transition: 'width 0.5s ease' }} />
            </div>
          </div>

          <div style={{ background: '#161F2E', border: '1px solid #1F2937', borderRadius: '8px', padding: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '6px' }}>
              <span style={{ color: '#9CA3AF' }}>Citation Coverage</span>
              <span style={{ color: '#06B6D4', fontWeight: 600 }}>92%</span>
            </div>
            <div style={{ width: '100%', height: '6px', background: '#1F2937', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: '92%', height: '100%', background: '#06B6D4' }} />
            </div>
          </div>
        </div>
      </div>

      {/* HITL Dialog Modal */}
      <HITLModal
        isOpen={isHitlOpen}
        onClose={() => setIsHitlOpen(false)}
        onApprove={() => handleApproveHitl()}
        onRefine={(prompt) => handleApproveHitl(prompt)}
        evaluatorFeedback={hitlData?.feedback}
        confidenceScore={hitlData?.score}
      />
    </div>
  );
};
