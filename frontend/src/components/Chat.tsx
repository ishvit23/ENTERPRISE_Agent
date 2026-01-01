import React, { useState, useRef } from 'react';
import { WS_BASE } from '../services/api';

const WS_URL = `${WS_BASE}/ws/qa`;

interface ChatProps {
  user?: any;
}

const Chat: React.FC<ChatProps> = ({ user }) => {
  const [messages, setMessages] = useState<Array<{role: string; text: string}>>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // user prop now comes from parent (App)

  const connectWS = () => {
    ws.current = new window.WebSocket(WS_URL);
    ws.current.onopen = () => {
      setConnected(true);
      setMessages(msgs => [...msgs, { role: 'system', text: 'Connected to assistant.' }]);
    };
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setIsTyping(false); // Stop typing animation when response received
      if (data.answer) {
        setMessages(msgs => [...msgs, { role: 'assistant', text: data.answer }]);
      } else if (data.error) {
        setMessages(msgs => [...msgs, { role: 'system', text: `Error: ${data.error}` }]);
      }
    };
    ws.current.onclose = () => {
      setConnected(false);
      setIsTyping(false);
      setMessages(msgs => [...msgs, { role: 'system', text: 'Disconnected.' }]);
    };
  };

  const sendMessage = () => {
    if (ws.current && connected && input.trim()) {
      setMessages(msgs => [...msgs, { role: 'user', text: input }]);
      setIsTyping(true); // Start typing animation
      ws.current.send(JSON.stringify({
        question: input,
        department: user.department,
        top_k: 5,
        user,
      }));
      setInput('');
      setTimeout(scrollToBottom, 100);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>💬 Enterprise Assistant</h2>
        <div className="chat-status">
          <span className={`chat-status-dot ${connected ? 'connected' : 'disconnected'}`}></span>
          {connected ? 'Online' : 'Offline'}
        </div>
      </div>
      {!connected && (
        <div style={{ padding: 20, textAlign: 'center' }}>
          <button onClick={connectWS} className="btn-primary">Connect to Assistant</button>
        </div>
      )}
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>
            <div className="chat-bubble">{msg.text}</div>
          </div>
        ))}
        {isTyping && (
          <div className="chat-message assistant">
            <div className="chat-bubble typing-indicator">
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input-area">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' ? sendMessage() : undefined}
          placeholder="Type your question..."
          disabled={!connected}
        />
        <button onClick={sendMessage} disabled={!connected}>Send</button>
      </div>
    </div>
  );
};

export default Chat;
