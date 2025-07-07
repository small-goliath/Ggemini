import axios from 'axios';
import { useState, useRef, useEffect } from 'react';
import './App.css';

interface ChatMessage {
  type: 'user' | 'bot';
  message: string;
}

// Header Component
const AppHeader = () => (
  <header className="app-header">
    <img src="/logo.png" alt="logo" className="logo" />
  </header>
);

// ChatHistory Component
const ChatHistory = ({ chatHistory, loading }: { chatHistory: ChatMessage[], loading: boolean }) => {
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, loading]);

  return (
    <div className="chat-history">
      {chatHistory.map((item, index) => (
        <div key={index} className={`message ${item.type}`}>
          <div className="content">{item.message}</div>
        </div>
      ))}
      {loading && (
        <div className="message bot">
          <div className="content">...</div>
        </div>
      )}
      <div ref={chatEndRef} />
    </div>
  );
};

// MessageInput Component
const MessageInput = ({
  question,
  setQuestion,
  handleSubmit,
  loading,
}: {
  question: string;
  setQuestion: (question: string) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  loading: boolean;
}) => (
  <form onSubmit={handleSubmit} className="message-input-form">
    <div className="input-group">
      <input
        type="text"
        className="form-control"
        placeholder="질문을 입력하세요."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        disabled={loading}
        aria-label="Question Input"
      />
      <button className="btn btn-primary" type="submit" disabled={loading}>
        {loading ? '분석 중...' : '전송'}
      </button>
    </div>
  </form>
);


function App() {
  const [question, setQuestion] = useState<string>('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!question.trim()) return;

    const newChatHistory: ChatMessage[] = [...chatHistory, { type: 'user', message: question }];
    setChatHistory(newChatHistory);
    setQuestion('');
    setLoading(true);

    try {
      const response = await axios.post<{ answer: string }>('http://localhost:8000/api/query', { question });
      setChatHistory([...newChatHistory, { type: 'bot', message: response.data.answer }]);
    } catch (error) {
      console.error('Error fetching answer:', error);
      setChatHistory([...newChatHistory, { type: 'bot', message: '알 수 없는 오류입니다.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <AppHeader />
      <ChatHistory chatHistory={chatHistory} loading={loading} />
      <MessageInput
        question={question}
        setQuestion={setQuestion}
        handleSubmit={handleSubmit}
        loading={loading}
      />
    </div>
  );
}

export default App;
