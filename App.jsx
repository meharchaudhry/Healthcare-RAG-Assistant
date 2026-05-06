import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import './index.css';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      type: 'bot',
      content: 'Hello! I am your Healthcare RAG assistant. How can I help you today?\n\nYou can ask me medical questions or upload a document if you want me to analyze something specific.'
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentFile, setCurrentFile] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleFileUpload = async (file) => {
    setIsLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentFile(file);
        setMessages(prev => [...prev, {
          id: Date.now(),
          type: 'system',
          content: `📄 "${file.name}" has been uploaded and added to my knowledge base. You can now ask questions about it.`
        }]);
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'error',
        content: `❌ Failed to upload ${file.name}. Please ensure the backend is running.`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (text) => {
    // Add user message
    const userMsg = { id: Date.now(), type: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text }),
      });

      if (!response.ok) throw new Error('Failed to fetch answer');

      const data = await response.json();

      const botMsg = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.answer,
        sources: data.sources || []
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      console.error('Error fetching answer:', err);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'error',
        content: "Sorry, I encountered an error getting the answer. Please try again."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header />

      <main className="chat-area">
        <div className="messages-list">
          {messages.map((msg, index) => (
            <ChatMessage
              key={msg.id}
              message={msg}
              isLatest={index === messages.length - 1}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="input-area">
        <div className="input-wrapper">
          <ChatInput
            onSendMessage={handleSendMessage}
            onFileUpload={handleFileUpload}
            isLoading={isLoading}
          />
          <div className="footer-credits">
            <p>© 2026 Healthcare RAG System</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
