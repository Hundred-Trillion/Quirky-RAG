"use client";

import { useState, useRef, useEffect } from 'react';

type Message = { role: 'user' | 'ai'; content: string };
type Document = { filename: string; active: boolean };

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'ai', content: 'Hello! I am Quirky RAG. Upload a PDF to get started, then ask me anything.' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const res = await fetch(`${API_URL}/documents/`);
      const data = await res.json();
      setDocuments(data.documents.map((d: string) => ({ filename: d, active: true })));
    } catch (e) {
      console.error(e);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      await fetch(`${API_URL}/ingest/`, {
        method: 'POST',
        body: formData,
      });
      fetchDocuments();
    } catch (e) {
      console.error(e);
    }
  };

  const toggleDoc = (i: number) => {
    const next = [...documents];
    next[i].active = !next[i].active;
    setDocuments(next);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsTyping(true);

    try {
      const activeDocs = documents.filter(d => d.active).map(d => d.filename);
      const res = await fetch(`${API_URL}/query/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg, active_documents: activeDocs, session_id: 'default' })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'ai', content: data.response }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'ai', content: 'There was an error connecting to the RAG backend.' }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <main className="layout">
      {/* Left Sidebar - Sessions */}
      <div className="glass-panel left-sidebar">
        <div className="panel-header">Sessions</div>
        <div className="panel-content">
          <div className="session-item active">Current Chat</div>
          <div className="session-item">Previous Analysis</div>
          <div className="session-item">Research Notes</div>
        </div>
      </div>

      {/* Center Chat */}
      <div className="glass-panel center-chat">
        <div className="panel-header">Quirky RAG ✨</div>
        <div className="panel-content">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <div className="message-bubble">{msg.content}</div>
            </div>
          ))}
          {isTyping && (
            <div className="message ai">
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
        <div className="input-area">
          <div className="input-container">
            <textarea 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about your documents..."
              rows={1}
            />
            <button className="send-btn" onClick={sendMessage}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Docs */}
      <div className="glass-panel right-sidebar">
        <div className="panel-header">Documents</div>
        <div className="panel-content">
          <input 
            type="file" 
            id="file-upload" 
            accept=".pdf" 
            style={{ display: 'none' }} 
            onChange={handleUpload} 
          />
          <button 
            className="upload-btn" 
            onClick={() => document.getElementById('file-upload')?.click()}
          >
            + Upload PDF
          </button>
          
          <div className="doc-list">
            {documents.length === 0 && <p style={{color: 'var(--text-secondary)', fontSize: '0.9rem'}}>No documents uploaded yet.</p>}
            {documents.map((doc, i) => (
              <div key={i} className="doc-item">
                <div className="doc-name">
                  <svg className="doc-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                  </svg>
                  {doc.filename.substring(0, 18) + (doc.filename.length > 18 ? '...' : '')}
                </div>
                <label className="toggle-switch">
                  <input type="checkbox" checked={doc.active} onChange={() => toggleDoc(i)} />
                  <span className="slider"></span>
                </label>
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
