export type AnalysisMode = 'demo' | 'llm';
export type Severity = 'high' | 'medium' | 'low';

export interface Finding {
  category: string;
  severity: Severity;
  title: string;
  evidence: string;
  explanation: string;
  recommendations: string[];
}

export interface Analysis {
  id: string;
  filename: string;
  created_at: string;
  mode: AnalysisMode;
  summary: string;
  findings: Finding[];
  next_steps: string[];
  redacted_excerpt: string;
  duration_ms: number;
}

export interface HistoryItem {
  id: string;
  created_at: string;
  filename: string;
  mode: AnalysisMode;
  summary: string;
  finding_count: number;
}

export interface Health {
  status: string;
  llm_enabled: boolean;
  max_log_bytes: number;
}
