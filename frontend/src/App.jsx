import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStepIdx, setLoadingStepIdx] = useState(0);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  const loadingSteps = [
    "Analyzing query parameters...",
    "Router classified destination",
    "Loading datasets to memory",
    "Extracting matching statistics",
    "Generating natural answer..."
  ];

  // Load history from localStorage on startup
  useEffect(() => {
    const cachedHistory = localStorage.getItem('college_agent_history');
    if (cachedHistory) {
      try {
        setHistory(JSON.parse(cachedHistory));
      } catch (e) {
        console.error("Failed to parse history cache", e);
      }
    }
  }, []);

  // Handle loading steps transitions
  useEffect(() => {
    let timer;
    if (isLoading) {
      setLoadingStepIdx(0);
      const scheduleNextStep = (idx) => {
        if (idx < loadingSteps.length - 1) {
          timer = setTimeout(() => {
            setLoadingStepIdx(idx + 1);
            scheduleNextStep(idx + 1);
          }, 300 + Math.random() * 150);
        }
      };
      scheduleNextStep(0);
    }
    return () => clearTimeout(timer);
  }, [isLoading]);

  const saveToHistory = (item) => {
    const updated = [item, ...history.filter(h => h.question !== item.question)].slice(0, 15);
    setHistory(updated);
    localStorage.setItem('college_agent_history', JSON.stringify(updated));
  };

  const handleQuery = async (queryText) => {
    if (!queryText.trim() || isLoading) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: queryText })
      });
      
      if (!res.ok) {
        throw new Error(`Server returned status code: ${res.status}`);
      }
      
      const data = await res.json();
      setResponse(data);
      saveToHistory({ question: queryText, ...data });
    } catch (err) {
      setError(err.message || "Failed to fetch response from backend.");
      setResponse(null);
    } finally {
      setIsLoading(false);
    }
  };

  const startNewChat = () => {
    setQuestion("");
    setResponse(null);
    setError(null);
  };

  // Simple clean markdown bold/list formatter
  const renderMarkdown = (text) => {
    if (!text) return null;
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      let formattedLine = line;
      const boldRegex = /\*\*(.*?)\*\*/g;
      let match;
      const parts = [];
      let lastIndex = 0;
      
      while ((match = boldRegex.exec(line)) !== null) {
        parts.push(line.substring(lastIndex, match.index));
        parts.push(<strong key={match.index}>{match[1]}</strong>);
        lastIndex = boldRegex.lastIndex;
      }
      parts.push(line.substring(lastIndex));
      
      const bulletMatch = line.match(/^(\*|-)\s+(.*)/);
      if (bulletMatch) {
        return (
          <li key={idx} style={{ marginLeft: '16px', marginBottom: '4px', listStyleType: 'circle' }}>
            {parts.map((p, pIdx) => {
              if (typeof p === 'string') {
                return p.replace(/^(\*|-)\s+/, '');
              }
              return p;
            })}
          </li>
        );
      }
      
      return <div key={idx} style={{ minHeight: '1.2em', marginBottom: '2px' }}>{parts}</div>;
    });
  };

  const isInitialState = !response && !isLoading && !error;

  return (
    <div className="app-layout">
      {/* Background Video */}
      <video autoPlay loop muted playsInline className="background-video">
        <source src="/video.mp4" type="video/mp4" />
      </video>

      {/* Sidebar for History */}
      <aside className="sidebar">
        <button className="new-chat-btn" onClick={startNewChat}>
          + New chat
        </button>
        <div className="history-section">
          <div className="history-title">Recent Queries</div>
          <div className="history-list">
            {history.map((h, idx) => (
              <div
                key={idx}
                className="history-item"
                onClick={() => {
                  setQuestion(h.question);
                  setResponse(h);
                  setError(null);
                }}
                title={h.question}
              >
                {h.question}
              </div>
            ))}
          </div>
        </div>
      </aside>

      {/* Main chat interface */}
      <main className="main-chat">
        <header className="chat-header">
          <div>College Analytics Assistant</div>
          <div className="app-version">v1.3.0</div>
        </header>

        <section className={`chat-messages ${isInitialState ? 'empty' : ''}`}>
          <div className="chat-messages-container">
            {isLoading ? (
              <div className="loading-logger">
                {loadingSteps.map((step, idx) => {
                  if (idx > loadingStepIdx) return null;
                  const isActive = idx === loadingStepIdx;
                  return (
                    <div key={idx} className="log-line">
                      {isActive ? <div className="log-spinner"></div> : "✓ "}
                      {step}
                    </div>
                  );
                })}
              </div>
            ) : error ? (
              <div className="message-block">
                <span className="message-sender">System Error</span>
                <div className="message-content" style={{ color: '#f87171' }}>
                  {error}
                </div>
              </div>
            ) : response ? (
              <>
                {/* User Prompt */}
                <div className="message-block">
                  <span className="message-sender">User</span>
                  <div className="message-content">{response.question}</div>
                </div>

                {/* Assistant Response */}
                <div className="message-block">
                  <span className="message-sender">Assistant</span>
                  <div className="message-content">
                    {renderMarkdown(response.answer)}
                    <div className="message-metadata">
                      Matched Institution: {response.matched_entity} | Source: {response.source}
                    </div>
                  </div>
                </div>
              </>
            ) : (
              /* Welcome / Empty State Screen with Centered Claude Input Bar */
              <div className="welcome-screen">
                <h2 className="welcome-title">College Analytics Assistant</h2>
                <p className="welcome-subtitle">Ask questions about official college fees, statistics, regulations, and cutoffs.</p>
                
                <div className="centered-input-bar">
                  <textarea
                    className="chat-textarea"
                    placeholder="Send a message..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleQuery(question);
                      }
                    }}
                  />
                  <button
                    className="send-arrow-btn"
                    onClick={() => handleQuery(question)}
                    disabled={isLoading || !question.trim()}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <line x1="22" y1="2" x2="11" y2="13"/>
                      <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                    </svg>
                  </button>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Bottom Dock Input Bar rendered only after welcome screen is dismissed */}
        {!isInitialState && (
          <section className="input-dock">
            <div className="input-bar">
              <textarea
                className="chat-textarea"
                placeholder="Send a message..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleQuery(question);
                  }
                }}
              />
              <button
                className="send-arrow-btn"
                onClick={() => handleQuery(question)}
                disabled={isLoading || !question.trim()}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <line x1="22" y1="2" x2="11" y2="13"/>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
              </button>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
