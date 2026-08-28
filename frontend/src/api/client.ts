export interface AgentStepEvent {
  thread_id: string;
  step_index: number;
  agent: 'supervisor' | 'rag' | 'research' | 'evaluator' | 'response' | 'human_node';
  title: string;
  thought: string;
  sources?: Array<{ title: string; url?: string; type: 'web' | 'kb'; score?: number }>;
  evaluation?: { score?: number; is_sufficient?: boolean; feedback?: string };
  execution_time_ms?: number;
}

export interface HitlCheckpointEvent {
  thread_id: string;
  feedback: string;
  score: number;
  status: string;
}

export interface FinalAnswerEvent {
  thread_id: string;
  final_answer: string;
  evaluation?: { score?: number; is_sufficient?: boolean; feedback?: string };
  status: string;
}

export interface KBDocument {
  id: string;
  name: string;
  type: string;
  size: string;
  status: string;
  summary: string;
}

export async function fetchKBDocuments(): Promise<KBDocument[]> {
  try {
    const res = await fetch('/api/documents');
    if (!res.ok) throw new Error('Failed to fetch KB documents');
    const data = await res.json();
    return data.documents || [];
  } catch (err) {
    console.warn('Using fallback document list:', err);
    return [
      { id: '1', name: 'multi_agent_rag_architecture.pdf', type: 'pdf', size: '2.4 MB', status: 'indexed', summary: 'System design specs' },
      { id: '2', name: 'langgraph_checkpoint_spec.md', type: 'markdown', size: '450 KB', status: 'indexed', summary: 'MemorySaver specs' },
    ];
  }
}

export async function streamResearchQuery(
  query: string,
  options: {
    threadId?: string;
    forceHitl?: boolean;
    onStep: (event: AgentStepEvent) => void;
    onHitl: (event: HitlCheckpointEvent) => void;
    onFinalAnswer: (event: FinalAnswerEvent) => void;
    onError: (err: any) => void;
  }
) {
  try {
    const response = await fetch('/api/research/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        thread_id: options.threadId,
        force_hitl: options.forceHitl ?? false,
      }),
    });

    if (!response.ok || !response.body) {
      throw new Error(`HTTP error ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    const processBlock = (block: string) => {
      const eventMatch = block.match(/event:\s*(.+)/);
      const dataMatch = block.match(/data:\s*(.+)/);

      if (eventMatch && dataMatch) {
        const eventType = eventMatch[1].trim();
        const eventData = JSON.parse(dataMatch[1].trim());

        if (eventType === 'agent_step') {
          options.onStep(eventData);
        } else if (eventType === 'hitl_checkpoint') {
          options.onHitl(eventData);
        } else if (eventType === 'final_answer') {
          options.onFinalAnswer(eventData);
        } else if (eventType === 'error') {
          options.onError(new Error(eventData.error || 'Research execution failed'));
        }
      }
    };

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split(/\r?\n\r?\n/);
      buffer = blocks.pop() || '';

      for (const block of blocks) {
        processBlock(block);
      }
    }

    // Process any residual event block left in buffer when stream completes
    if (buffer.trim()) {
      processBlock(buffer);
    }
  } catch (err) {
    console.error('SSE Stream Error:', err);
    options.onError(err);
  }
}

export async function approveHitlCheckpoint(threadId: string, feedback?: string) {
  const res = await fetch('/api/research/approve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      thread_id: threadId,
      human_feedback: feedback,
    }),
  });

  if (!res.ok) {
    throw new Error(`Failed to approve HITL checkpoint: ${res.statusText}`);
  }

  return await res.json();
}
