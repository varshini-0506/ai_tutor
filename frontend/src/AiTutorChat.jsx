import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

// Parse Gemini markdown-style quiz format
function parseMarkdownQuiz(text) {
  // Split by questions
  const questionBlocks = text.split(/\*\*Question \d+:\*\*/g).map(b => b.trim()).filter(Boolean);
  return questionBlocks.map(block => {
    // Remove the correct answer line from the block before extracting options
    const blockWithoutAnswer = block.replace(/\*\*Correct Answer:\*\*.*$/gim, '').trim();
    // Extract question text (up to first option)
    const qMatch = blockWithoutAnswer.match(/^(.*?)([a-d]\))/is);
    const question = qMatch ? qMatch[1].replace(/\n/g, ' ').trim() : blockWithoutAnswer;
    // Extract options (capture everything after the letter, including markdown)
    const options = [];
    const optionRegex = /([a-d])\)\s+([\s\S]*?)(?=\n[a-d]\)|$)/gi;
    let optMatch;
    while ((optMatch = optionRegex.exec(blockWithoutAnswer))) {
      options.push({ key: optMatch[1], text: optMatch[2].trim() });
    }
    // Extract correct answer from the original block
    const ansMatch = block.match(/\*\*Correct Answer:\*\*\s*([a-d]\))/i);
    const answer = ansMatch ? ansMatch[1][0] : null;
    return { question, options, answer };
  }).filter(q => q.options && q.options.length > 0);
}

function QuizMessage({ text }) {
  const quizBlocks = parseMarkdownQuiz(text);
  if (!quizBlocks.length) return <div>{text}</div>;
  return (
    <div style={{ marginBottom: 8 }}>
      {quizBlocks.map((block, idx) => (
        <QuizBlock key={idx} {...block} number={idx + 1} />
      ))}
    </div>
  );
}

function QuizBlock({ question, options, answer, number }) {
  const [selected, setSelected] = useState(null);
  const [result, setResult] = useState(null);
  const handleSelect = (key) => {
    setSelected(key);
    setResult(key === answer ? 'Correct!' : 'Wrong!');
  };
  return (
    <div style={{ marginBottom: 16, padding: 8, background: '#f3f4f6', borderRadius: 8 }}>
      <div style={{ fontWeight: 600, marginBottom: 6 }}>{question}</div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {options.map(opt => (
          <button
            key={opt.key}
            onClick={() => handleSelect(opt.key)}
            disabled={!!selected}
            style={{
              background: selected === opt.key ? (selected === answer ? '#d1fae5' : '#fee2e2') : '#f4f4f4',
              border: '1px solid #ccc',
              borderRadius: 6,
              padding: '6px 12px',
              cursor: selected ? 'not-allowed' : 'pointer',
              fontWeight: selected === opt.key ? 700 : 400,
              textAlign: 'left',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              color: '#222',
            }}
          >
            <span style={{ fontWeight: 700, minWidth: 24 }}>{opt.key})</span>
            <span style={{ flex: 1, textAlign: 'left' }}><ReactMarkdown>{opt.text}</ReactMarkdown></span>
          </button>
        ))}
      </div>
      {selected && <div style={{ marginTop: 8, fontWeight: 600 }}>{result}</div>}
    </div>
  );
}

export default function AiTutorChat({ token }) {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [action, setAction] = useState('text');

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!question) return;
    setLoading(true);
    setMessages([...messages, { from: 'user', text: question, action }]);
    const body = { message: question, action };
    const res = await fetch('http://127.0.0.1:5000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(token && { Authorization: `Bearer ${token}` }) },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    setMessages(msgs => [...msgs, { from: 'ai', text: data.reply, action }]);
    setQuestion('');
    setLoading(false);
  };

  // Helper to render markdown with code highlighting
  function MarkdownWithCode({ children }) {
    return (
      <ReactMarkdown
        children={children}
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline ? (
              <SyntaxHighlighter style={oneLight} language={match?.[1] || 'python'} PreTag="div" {...props}>
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className={className} {...props}>{children}</code>
            );
          }
        }}
      />
    );
  }

  return (
    <div style={{
      maxWidth: 600, margin: '2rem auto', background: '#fff', borderRadius: 12,
      boxShadow: '0 2px 16px rgba(0,0,0,0.08)', padding: '2rem', height: '80vh', display: 'flex', flexDirection: 'column'
    }}>
      <h2>AI Tutor Chat</h2>
      <form onSubmit={sendMessage} style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <select value={action} onChange={e => setAction(e.target.value)} style={{ borderRadius: 6, padding: 6 }}>
            <option value="text">Text</option>
            <option value="code">Code</option>
            <option value="diagram">Diagram</option>
            <option value="quiz">Quiz</option>
          </select>
          <input
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="Ask a question..."
            style={{ borderRadius: 6, border: '1px solid #ccc', padding: 8, flex: 1 }}
            required
          />
        </div>
        <button type="submit" disabled={loading}>{loading ? 'Thinking...' : 'Ask AI'}</button>
      </form>
      <div style={{ flex: 1, overflowY: 'auto', paddingRight: 8 }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            background: msg.from === 'ai' ? '#e0e7ff' : '#f8f9fa',
            borderRadius: 8,
            padding: 10,
            marginBottom: 8,
            textAlign: msg.from === 'ai' ? 'left' : 'right',
            border: msg.from === 'ai' ? '1px solid #b4b8ff' : '1px solid #e5e7eb',
            fontSize: 16
          }}>
            <strong>{msg.from === 'ai' ? 'AI' : 'You'}{msg.action ? ` (${msg.action})` : ''}:</strong>{' '}
            {msg.from === 'ai' && msg.action === 'quiz' ? (
              <QuizMessage text={msg.text} />
            ) : msg.from === 'ai' ? (
              <MarkdownWithCode>{msg.text}</MarkdownWithCode>
            ) : (
              msg.text
            )}
          </div>
        ))}
      </div>
    </div>
  );
} 