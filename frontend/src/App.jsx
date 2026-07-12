import { useState, useEffect, useRef, forwardRef } from 'react';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

const SUGGESTIONS = [
  'Top engineering colleges in Jharkhand',
  'Compare NIT Jamshedpur and Birla Institute of Technology Mesra',
  'Show government colleges in Jharkhand',
  'Colleges under Rs. 1.5 lakh fees',
  'Hostel and mess details of BIT Sindri',
  'Colleges with average package above 8 LPA',
];

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
      {/* Pulse logo stage */}
      <div className="splash-stage">
        <img src="/logo.svg" alt="Logo" className="splash-logo-pulse" />
      </div>

      {/* Wordmark */}
      <div className="splash-wordmark">
        <span>Jharkhand Campus Agent</span>
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
    const parts = [];
    let key = 0;
    const rx = /\*\*(.*?)\*\*|`([^`]+)`/g;
    let last = 0, m;
    while ((m = rx.exec(line)) !== null) {
      if (m.index > last) parts.push(line.slice(last, m.index));
      if (m[1] !== undefined) parts.push(<strong key={key++}>{m[1]}</strong>);
      if (m[2] !== undefined) parts.push(<code key={key++}>{m[2]}</code>);
      last = rx.lastIndex;
    }
    parts.push(line.slice(last));
    return parts;
  };

  lines.forEach((line, idx) => {
    const heading = line.match(/^(#{1,3})\s+(.*)/);
    if (heading) {
      flushList(idx);
      elements.push(<h3 key={idx}>{parseLine(heading[2])}</h3>);
      return;
    }
    const bullet = line.match(/^(\*|-|\d+\.)\s+(.*)/);
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
  // Each conversation: { id: string, title: string, messages: [{role, content, meta?}] }
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId]   = useState(null);
  const [inputVal, setInputVal]           = useState('');
  const [isLoading, setIsLoading]         = useState(false);
  const [stepIdx, setStepIdx]             = useState(0);
  const [error, setError]                 = useState(null);
  const [showSplash, setShowSplash]       = useState(true);

  const textareaRef = useRef(null);
  const bottomRef   = useRef(null);
  useAutoGrow(textareaRef, inputVal);

  // Restore conversations from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('campus_convs');
      if (saved) {
        const convs = JSON.parse(saved);
        setConversations(convs);
        if (convs.length > 0) setActiveConvId(convs[0].id);
      }
    } catch {}
  }, []);

  // Persist conversations
  useEffect(() => {
    try { localStorage.setItem('campus_convs', JSON.stringify(conversations)); } catch {}
  }, [conversations]);

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

  // Scroll to bottom on new messages / loading
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversations, isLoading, error]);

  const activeConv = conversations.find(c => c.id === activeConvId) ?? null;
  const messages   = activeConv?.messages ?? [];
  const isWelcome  = messages.length === 0 && !isLoading && !error;

  const startNew = () => {
    const id   = Date.now().toString();
    const conv = { id, title: 'New chat', messages: [] };
    setConversations(prev => [conv, ...prev]);
    setActiveConvId(id);
    setInputVal('');
    setError(null);
  };

  const handleQuery = async (q) => {
    const query = (q || inputVal).trim();
    if (!query || isLoading) return;

    // Auto-create a conversation if none is active
    let convId = activeConvId;
    if (!convId || !conversations.find(c => c.id === convId)) {
      const id   = Date.now().toString();
      const conv = { id, title: query.slice(0, 45), messages: [] };
      setConversations(prev => [conv, ...prev]);
      setActiveConvId(id);
      convId = id;
    }

    const userMsg = { role: 'user', content: query };
    setConversations(prev => prev.map(c =>
      c.id === convId
        ? {
            ...c,
            title:    c.messages.length === 0 ? query.slice(0, 45) : c.title,
            messages: [...c.messages, userMsg],
          }
        : c
    ));

    setInputVal('');
    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ question: query }),
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data = await res.json();

      const assistantMsg = { role: 'assistant', content: data.answer, meta: data };
      setConversations(prev => prev.map(c =>
        c.id === convId
          ? { ...c, messages: [...c.messages, assistantMsg] }
          : c
      ));
    } catch (e) {
      setError(e.message || 'Failed to reach backend.');
    } finally {
      setIsLoading(false);
    }
  };

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
          <span className="sidebar-brand-text">Campus Agent (JH)</span>
        </div>

        <button className="new-chat-btn" onClick={startNew}>
          <IconPlus /> New chat
        </button>

        <div className="history-label">Conversations</div>
        <div className="history-list">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              className={`history-item ${conv.id === activeConvId ? 'active' : ''}`}
              title={conv.title}
              onClick={() => { setActiveConvId(conv.id); setInputVal(''); setError(null); }}
            >
              {conv.title}
            </div>
          ))}
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="main-chat">
        <header className="chat-header">
          <span className="header-title">Jharkhand Campus Assistant — College Discovery</span>
          <span className="header-badge">v2.0</span>
        </header>

        <div className={`chat-messages ${isWelcome ? 'empty' : ''}`}>
          <div className="chat-messages-container">

            {/* Welcome state */}
            {isWelcome && (
              <div className="welcome-screen">
                <div className="welcome-glow">
                  <img src="/logo.svg" alt="Campus Agent" width="44" height="44" />
                </div>
                <h1 className="welcome-title">Find your college.</h1>
                <p className="welcome-subtitle">
                  Ask about rankings, fees, placements, hostels and more — specifically for Jharkhand engineering colleges.
                </p>
                <div className="suggestion-chips">
                  {SUGGESTIONS.map((s) => (
                    <button key={s} className="suggestion-chip" onClick={() => handleQuery(s)}>
                      {s}
                    </button>
                  ))}
                </div>
                <div className="centered-input-wrap" style={{ marginTop: 24 }}>
                  <InputBox
                    value={inputVal}
                    onChange={setInputVal}
                    onSubmit={() => handleQuery()}
                    isLoading={isLoading}
                    ref={textareaRef}
                  />
                </div>
              </div>
            )}

            {/* Message thread for the active conversation */}
            {messages.map((msg, i) =>
              msg.role === 'user'
                ? <UserBubble key={i} text={msg.content} />
                : <AssistantBubble key={i} response={{ answer: msg.content, ...msg.meta }} />
            )}

            {/* Loading */}
            {isLoading && (
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
            )}

            {/* Error */}
            {error && !isLoading && (
              <div className="error-bubble">{error}</div>
            )}

          </div>
          <div ref={bottomRef} />
        </div>

        {/* Docked input (after welcome) */}
        {!isWelcome && (
          <div className="input-dock">
            <div className="input-dock-inner">
              <InputBox
                value={inputVal}
                onChange={setInputVal}
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
