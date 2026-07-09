import { useState, useEffect, useRef, forwardRef } from 'react';
import './App.css';

// ── Splash Screen ─────────────────────────────────────────────
function SplashScreen({ onDone }) {
  const [fading, setFading] = useState(false);

  useEffect(() => {
    const fadeTimer = setTimeout(() => setFading(true), 2400);
    const doneTimer = setTimeout(() => onDone(), 2950);
    return () => { clearTimeout(fadeTimer); clearTimeout(doneTimer); };
  }, [onDone]);

  return (
    <div className={`splash ${fading ? 'splash--out' : ''}`}>

      {/* ── Morphing icon stage ── */}
      <div className="splash-stage">

        {/* 1 — Bicycle */}
        <svg className="splash-icon splash-icon--1" viewBox="0 0 48 48" fill="none"
          stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="36" r="9"/>
          <circle cx="36" cy="36" r="9"/>
          <circle cx="22" cy="30" r="2" fill="currentColor"/>
          <line x1="22" y1="30" x2="12" y2="36"/>
          <line x1="22" y1="30" x2="36" y2="36"/>
          <line x1="20" y1="16" x2="22" y2="30"/>
          <line x1="20" y1="16" x2="34" y2="20"/>
          <line x1="34" y1="20" x2="22" y2="30"/>
          <line x1="34" y1="20" x2="36" y2="36"/>
          <line x1="15" y1="14" x2="23" y2="14"/>
          <line x1="19" y1="14" x2="20" y2="16"/>
          <line x1="32" y1="17" x2="38" y2="17"/>
          <line x1="36" y1="15" x2="34" y2="20"/>
        </svg>

        {/* 2 — Golf bag */}
        <svg className="splash-icon splash-icon--2" viewBox="0 0 48 48" fill="none"
          stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M17,18 Q15,18 14,20 L12,42 Q12,44 14,44 L34,44 Q36,44 36,42 L34,20 Q33,18 31,18 Z"/>
          <line x1="17" y1="18" x2="31" y2="18"/>
          <line x1="20" y1="9" x2="20" y2="18"/>
          <line x1="24" y1="7" x2="24" y2="18"/>
          <line x1="28" y1="9" x2="28" y2="18"/>
          <circle cx="20" cy="8.5" r="1.5"/>
          <circle cx="24" cy="6.5" r="1.5"/>
          <circle cx="28" cy="8.5" r="1.5"/>
          <path d="M16,26 Q24,22 32,30"/>
          <line x1="18" y1="44" x2="16" y2="47"/>
          <line x1="30" y1="44" x2="32" y2="47"/>
        </svg>

        {/* 3 — Coffee mug */}
        <svg className="splash-icon splash-icon--3" viewBox="0 0 48 48" fill="none"
          stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M10,22 L10,42 Q10,44 12,44 L34,44 Q36,44 36,42 L36,22 Z"/>
          <line x1="8" y1="22" x2="38" y2="22"/>
          <path d="M36,28 Q45,28 45,35 Q45,42 36,42"/>
          <path d="M18,17 Q20,12 18,7"/>
          <path d="M24,17 Q26,12 24,7"/>
          <path d="M30,17 Q32,12 30,7"/>
        </svg>

        {/* 4 — Laptop */}
        <svg className="splash-icon splash-icon--4" viewBox="0 0 48 48" fill="none"
          stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <rect x="6" y="5" width="36" height="26" rx="2"/>
          <rect x="10" y="9" width="28" height="18" rx="1"/>
          <rect x="2" y="31" width="44" height="9" rx="2"/>
          <line x1="6" y1="31" x2="42" y2="31"/>
          <rect x="17" y="34" width="14" height="4" rx="1"/>
        </svg>

      </div>

      {/* Wordmark */}
      <div className="splash-wordmark">
        <img src="/logo.svg" alt="" width="22" height="22" />
        <span>Campus Agent</span>
      </div>

      {/* Bottom progress line */}
      <div className="splash-bar"><div className="splash-bar-fill" /></div>
    </div>
  );
}

// ── Icons ──────────────────────────────────────────────────────
const IconSend = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13"/>
    <polygon points="22 2 15 22 11 13 2 9 22 2"/>
  </svg>
);

const IconPlus = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
  </svg>
);

const IconCheck = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);


// ── Loading steps ──────────────────────────────────────────────
const LOADING_STEPS = [
  'Analyzing query intent',
  'Routing to specialized node',
  'Querying knowledge base',
  'Extracting matched records',
  'Generating response',
];


// ── Markdown renderer ──────────────────────────────────────────
function renderMarkdown(text) {
  if (!text) return null;
  const lines = text.split('\n');
  const elements = [];
  let listBuffer = [];

  const flushList = (key) => {
    if (listBuffer.length > 0) {
      elements.push(<ul key={`ul-${key}`}>{listBuffer}</ul>);
      listBuffer = [];
    }
  };

  const parseLine = (line) => {
    const boldRx = /\*\*(.*?)\*\*/g;
    const parts = [];
    let last = 0, m;
    while ((m = boldRx.exec(line)) !== null) {
      if (m.index > last) parts.push(line.slice(last, m.index));
      parts.push(<strong key={m.index}>{m[1]}</strong>);
      last = boldRx.lastIndex;
    }
    parts.push(line.slice(last));
    return parts;
  };

  lines.forEach((line, idx) => {
    const bullet = line.match(/^(\*|-)\s+(.*)/);
    if (bullet) {
      listBuffer.push(<li key={idx}>{parseLine(bullet[2])}</li>);
    } else {
      flushList(idx);
      if (line.trim() === '') {
        elements.push(<div key={idx} style={{ height: '0.5em' }} />);
      } else {
        elements.push(<div key={idx}>{parseLine(line)}</div>);
      }
    }
  });
  flushList('end');
  return elements;
}

// ── Auto-grow textarea hook ────────────────────────────────────
function useAutoGrow(ref, value) {
  useEffect(() => {
    if (!ref.current) return;
    ref.current.style.height = 'auto';
    ref.current.style.height = `${ref.current.scrollHeight}px`;
  }, [ref, value]);
}

// ── Main App ───────────────────────────────────────────────────
export default function App() {
  const [question, setQuestion]     = useState('');
  const [response, setResponse]     = useState(null);
  const [isLoading, setIsLoading]   = useState(false);
  const [stepIdx, setStepIdx]       = useState(0);
  const [error, setError]           = useState(null);
  const [history, setHistory]       = useState([]);
  const [showSplash, setShowSplash] = useState(true);

  const textareaRef = useRef(null);
  const bottomRef   = useRef(null);
  useAutoGrow(textareaRef, question);

  // Restore history
  useEffect(() => {
    try {
      const h = localStorage.getItem('campus_agent_history');
      if (h) setHistory(JSON.parse(h));
    } catch {}
  }, []);

  // Animated loading steps
  useEffect(() => {
    if (!isLoading) return;
    setStepIdx(0);
    let i = 0;
    const tick = () => {
      if (i < LOADING_STEPS.length - 1) {
        i++;
        setStepIdx(i);
        setTimeout(tick, 400 + Math.random() * 200);
      }
    };
    const t = setTimeout(tick, 420);
    return () => clearTimeout(t);
  }, [isLoading]);

  const saveHistory = (item) => {
    const updated = [item, ...history.filter(h => h.question !== item.question)].slice(0, 15);
    setHistory(updated);
    localStorage.setItem('campus_agent_history', JSON.stringify(updated));
  };

  const handleQuery = async (q) => {
    const query = (q || question).trim();
    if (!query || isLoading) return;
    setIsLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: query }),
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data = await res.json();
      const item = { question: query, ...data };
      setResponse(item);
      saveHistory(item);
    } catch (e) {
      setError(e.message || 'Failed to reach backend.');
    } finally {
      setIsLoading(false);
    }
  };

  const startNew = () => {
    setQuestion('');
    setResponse(null);
    setError(null);
  };

  const isWelcome = !response && !isLoading && !error;

  return (
    <div className="app-layout">
      {/* Background video */}
      <video autoPlay loop muted playsInline className="background-video">
        <source src="/video.mp4" type="video/mp4" />
      </video>

      {/* ── Splash Screen ── */}
      {showSplash && <SplashScreen onDone={() => setShowSplash(false)} />}

      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">
            <img src="/logo.svg" alt="Campus Agent logo" width="18" height="18" />
          </div>
          <span className="sidebar-brand-text">Campus Agent</span>
        </div>

        <button className="new-chat-btn" onClick={startNew}>
          <IconPlus /> New chat
        </button>

        <div className="history-label">Recent</div>
        <div className="history-list">
          {history.map((h, i) => (
            <div
              key={i}
              className="history-item"
              title={h.question}
              onClick={() => { setQuestion(h.question); setResponse(h); setError(null); }}
            >
              {h.question}
            </div>
          ))}
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="main-chat">
        <header className="chat-header">
          <span className="header-title">College Analytics Assistant</span>
          <span className="header-badge">v1.4</span>
        </header>

        <div className={`chat-messages ${isWelcome ? 'empty' : ''}`}>
          <div className="chat-messages-container">

            {/* Welcome state */}
            {isWelcome && (
              <div className="welcome-screen">
                <div className="welcome-glow">
                  <img src="/logo.svg" alt="Campus Agent" width="44" height="44" />
                </div>
                <h1 className="welcome-title">What can I help with?</h1>
                <p className="welcome-subtitle">
                  Ask about college fees, NIRF rankings, scholarship eligibility, placements, and exam policies.
                </p>
                <div className="centered-input-wrap">
                  <InputBox
                    value={question}
                    onChange={setQuestion}
                    onSubmit={() => handleQuery()}
                    isLoading={isLoading}
                    ref={textareaRef}
                  />
                </div>
              </div>
            )}

            {/* Loading */}
            {isLoading && (
              <>
                <UserBubble text={question} />
                <div className="loading-block">
                  {LOADING_STEPS.map((step, i) => {
                    if (i > stepIdx) return null;
                    const isDone   = i < stepIdx;
                    const isActive = i === stepIdx;
                    return (
                      <div key={i} className={`log-line ${isDone ? 'done' : isActive ? 'active' : ''}`}>
                        {isDone
                          ? <div className="log-check"><IconCheck /></div>
                          : <div className="log-pulse" />
                        }
                        {step}
                      </div>
                    );
                  })}
                </div>
              </>
            )}

            {/* Error */}
            {error && !isLoading && (
              <div className="error-bubble">{error}</div>
            )}

            {/* Response */}
            {response && !isLoading && (
              <>
                <UserBubble text={response.question} />
                <AssistantBubble response={response} />
              </>
            )}

          </div>
          <div ref={bottomRef} />
        </div>

        {/* Docked input (after welcome) */}
        {!isWelcome && (
          <div className="input-dock">
            <div className="input-dock-inner">
              <InputBox
                value={question}
                onChange={setQuestion}
                onSubmit={() => handleQuery()}
                isLoading={isLoading}
                ref={textareaRef}
              />
              <div className="input-hint">Enter to send · Shift+Enter for new line</div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

// ── Sub-components ─────────────────────────────────────────────

function UserBubble({ text }) {
  return (
    <div className="msg-row user">
      <div className="msg-bubble">
        <div className="msg-label">You</div>
        <div className="msg-text">{text}</div>
      </div>
    </div>
  );
}

function AssistantBubble({ response }) {
  return (
    <div className="msg-row assistant">
      <div className="msg-bubble">
        <div className="msg-label">Assistant</div>
        <div className="msg-text">{renderMarkdown(response.answer)}</div>
        <div className="msg-meta">
          {response.matched_entity && response.matched_entity !== 'Unknown' && (
            <span className="meta-pill"><span>Matched</span>{response.matched_entity}</span>
          )}
          {response.source && (
            <span className="meta-pill"><span>Source</span>{response.source}</span>
          )}
          {response.intent && (
            <span className="meta-pill"><span>Intent</span>{response.intent}</span>
          )}
        </div>
      </div>
    </div>
  );
}



const InputBox = forwardRef(function InputBox({ value, onChange, onSubmit, isLoading }, ref) {
  return (
    <div className="input-container">
      <textarea
        ref={ref}
        className="chat-textarea"
        placeholder="Ask about colleges, fees, scholarships…"
        value={value}
        rows={1}
        onChange={e => onChange(e.target.value)}
        onKeyDown={e => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            onSubmit();
          }
        }}
      />
      <button
        className="send-btn"
        onClick={onSubmit}
        disabled={isLoading || !value.trim()}
      >
        <IconSend />
      </button>
    </div>
  );
});
