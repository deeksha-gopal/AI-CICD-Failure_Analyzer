import { useEffect, useRef, useState } from 'react';
import { analyzeLog, getAnalysis, getHealth, getHistory } from './api';
import type { Analysis, AnalysisMode, Health, HistoryItem } from './types';

const SAMPLE = `2026-10-22T08:45:10Z [CI] Run pytest -q
=================================== FAILURES ===================================
FAILED tests/test_payment.py::test_total - AssertionError: assert 21 == 20
ModuleNotFoundError: No module named 'requests'
Error: Process completed with exit code 1.`;

function formatDate(value: string): string {
  return new Date(value).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}

export default function App() {
  const [mode, setMode] = useState<AnalysisMode>('demo');
  const [logText, setLogText] = useState(SAMPLE);
  const [filename, setFilename] = useState('sample-pipeline.log');
  const [health, setHealth] = useState<Health | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [report, setReport] = useState<Analysis | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  async function refreshHistory() {
    try { setHistory(await getHistory()); } catch { /* Keep UI usable offline */ }
  }

  useEffect(() => {
    void getHealth().then(setHealth).catch(() => setHealth(null));
    void refreshHistory();
  }, []);

  async function readFile(file: File | undefined) {
    if (!file) return;
    setError('');
    if (!/\.(log|txt)$/i.test(file.name)) { setError('Choose a .log or .txt file.'); return; }
    if (file.size > 256 * 1024) { setError('Maximum file size is 256 KiB.'); return; }
    setFilename(file.name);
    setLogText(await file.text());
  }

  async function runAnalysis() {
    setError('');
    if (!logText.trim()) { setError('Paste a log or upload a file first.'); return; }
    setLoading(true);
    try {
      const file = new File([logText], filename, { type: 'text/plain' });
      const result = await analyzeLog(file, mode);
      setReport(result);
      void refreshHistory();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Analysis failed.');
    } finally {
      setLoading(false);
    }
  }

  async function openHistory(id: string) {
    setError('');
    try { setReport(await getAnalysis(id)); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Cannot load analysis.'); }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-symbol">⌘</span><div><strong>PipelineLens</strong><small>CI/CD Intelligence</small></div></div>
        <div className="nav-heading">WORKSPACE</div>
        <div className="nav-item selected">▦ &nbsp; Analyzer <span>LIVE</span></div>
        <div className="nav-item">▤ &nbsp; Analysis history</div>
        <div className="sidebar-divider" />
        <div className="sidebar-caption">RECENT ANALYSES</div>
        <div className="history-list">
          {history.length === 0 ? <p className="sidebar-empty">Run an analysis to create history.</p> : history.map(item => (
            <button className="history-entry" type="button" key={item.id} onClick={() => void openHistory(item.id)}>
              <span className="history-dot" /><span className="history-info"><strong>{item.filename}</strong><small>{formatDate(item.created_at)}</small></span>
            </button>
          ))}
        </div>
        <div className="sidebar-footer"><span className="status-dot" /> {health ? 'API connected' : 'API offline'}<small>Open-source portfolio project · v1.0</small></div>
      </aside>

      <main className="main">
        <header className="topbar"><div className="breadcrumb">Engineering tools <span>/</span> <strong>Failure analyzer</strong></div><div className="chip">⚡ DevOps + AI</div></header>
        <div className="content">
          <div className="intro"><div className="eyebrow">DEVELOPER PRODUCTIVITY / AI ASSISTANT</div><h1>Debug pipelines.<br /><em>Ship with confidence.</em></h1><p>Turn noisy CI/CD failure logs into actionable, evidence-backed troubleshooting steps. Local rule-based analysis works instantly; connect an LLM for deeper suggestions.</p></div>
          <div className="metrics"><div className="metric"><span>ANALYSES SAVED</span><strong>{history.length}</strong><small>Up to 25 recent</small></div><div className="metric"><span>LAST FINDINGS</span><strong>{report?.findings.length ?? '—'}</strong><small>Potential causes</small></div><div className="metric"><span>BACKEND STATUS</span><strong className="metric-status">{health ? 'Online' : 'Offline'}</strong><small>{health?.llm_enabled ? 'LLM mode available' : 'Demo mode available'}</small></div></div>

          <div className="grid-layout">
            <section className="panel input-panel">
              <div className="panel-heading"><div><div className="section-kicker">01 / INPUT</div><h2>Analyze a pipeline log</h2></div><span className="panel-icon">⌁</span></div>
              <label className="field-label" htmlFor="log-content">CI/CD log output</label>
              <textarea id="log-content" spellCheck={false} value={logText} onChange={event => setLogText(event.target.value)} aria-describedby="upload-note" placeholder="Paste Jenkins, GitHub Actions, or other CI logs here..." />
              <div className="textarea-footer"><span id="upload-note">{filename} · {new TextEncoder().encode(logText).length.toLocaleString()} bytes</span><button type="button" className="link-button" onClick={() => { setFilename('sample-pipeline.log'); setLogText(SAMPLE); }}>Load sample</button></div>
              <input ref={fileRef} hidden type="file" accept=".log,.txt,text/plain" onChange={event => void readFile(event.target.files?.[0])} />
              <button className="upload-btn" type="button" onClick={() => fileRef.current?.click()}>↑ &nbsp; Upload .log or .txt file</button>
              <div className="field-label mode-label">Analysis engine</div>
              <div className="segmented" role="group" aria-label="Analysis engine"><button className={mode === 'demo' ? 'active' : ''} onClick={() => setMode('demo')}>◇ &nbsp; Smart rules <small>No API key</small></button><button className={mode === 'llm' ? 'active' : ''} onClick={() => setMode('llm')} disabled={!health?.llm_enabled}>✦ &nbsp; LLM analysis <small>{health?.llm_enabled ? 'Enabled' : 'Requires API key'}</small></button></div>
              {error && <div className="error-banner" role="alert">{error}</div>}
              <button className="analyze-button" type="button" onClick={() => void runAnalysis()} disabled={loading || !health}>{loading ? 'Analyzing…' : 'Analyze failure'} <span>→</span></button>
              <p className="safety-note">Logs are redacted with best-effort patterns before being stored or sent to an LLM. Do not upload confidential logs or credentials. No diagnosis is guaranteed.</p>
            </section>
            <section className="panel report-panel">
              <div className="panel-heading"><div><div className="section-kicker">02 / OUTPUT</div><h2>Diagnostic report</h2></div>{report && <span className="pill">{report.mode === 'llm' ? 'AI analyzed' : 'Rule-based'}</span>}</div>
              {!report ? <div className="empty-state"><div className="empty-art">{`{ }`}</div><h3>Ready to investigate</h3><p>Paste a pipeline failure or upload a log and select <strong>Analyze failure</strong>. Findings and next steps will appear here.</p><div className="empty-line" /><div className="empty-line short" /></div> : <div className="result">
                <div className="report-meta"><span>✓ Analysis complete</span><small>{report.duration_ms} ms · {formatDate(report.created_at)}</small></div>
                <div className="summary"><div className="mini-label">SUMMARY</div><p>{report.summary}</p></div>
                <div className="mini-label findings-title">POTENTIAL FINDINGS <span>{report.findings.length}</span></div>
                {report.findings.map((finding, idx) => <article className="finding" key={`${finding.category}-${idx}`}><div className="finding-heading"><span className={`severity ${finding.severity}`}>{finding.severity.toUpperCase()}</span><span className="category">{finding.category}</span></div><h3>{finding.title}</h3><code>{finding.evidence}</code><p>{finding.explanation}</p><ul>{finding.recommendations.map((step, index) => <li key={index}>{step}</li>)}</ul></article>)}
                <div className="next-steps"><div className="mini-label">NEXT STEPS</div><ol>{report.next_steps.map((step, index) => <li key={index}>{step}</li>)}</ol></div>
              </div>}
            </section>
          </div>
          <footer className="footer">Built with React · TypeScript · FastAPI · SQLAlchemy · Docker <span>⚡ AI features require your own API key</span></footer>
        </div>
      </main>
    </div>
  );
}
