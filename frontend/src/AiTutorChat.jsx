import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

// Parse Gemini markdown-style quiz format
function parseMarkdownQuiz(text) {
  const questionBlocks = text.split(/\*\*Question \d+:\*\*/g).map(b => b.trim()).filter(Boolean);
  return questionBlocks.map(block => {
    const blockWithoutAnswer = block.replace(/\*\*Correct Answer:\*\*.*$/gim, '').trim();
    const qMatch = blockWithoutAnswer.match(/^(.*?)([a-d]\))/is);
    const question = qMatch ? qMatch[1].replace(/\n/g, ' ').trim() : blockWithoutAnswer;
    const options = [];
    const optionRegex = /([a-d])\)\s+([\s\S]*?)(?=\n[a-d]\)|$)/gi;
    let optMatch;
    while ((optMatch = optionRegex.exec(blockWithoutAnswer))) {
      options.push({ key: optMatch[1], text: optMatch[2].trim() });
    }
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
  const [imageFile, setImageFile] = useState(null);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!question && action !== 'image') return;
    setLoading(true);
    setMessages([...messages, { from: 'user', text: question, action }]);

    // Handle image upload as base64 in JSON
    if (action === 'image' && imageFile) {
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64String = reader.result;
        try {
          const res = await fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...(token && { Authorization: `Bearer ${token}` }) },
            body: JSON.stringify({ message: base64String, action: 'image' })
          });
          const contentType = res.headers.get('content-type');
          let data;
          if (contentType && contentType.includes('application/json')) {
            data = await res.json();
          } else {
            const text = await res.text();
            throw new Error('Non-JSON response: ' + text);
          }
          setMessages(msgs => [...msgs, { from: 'ai', text: data.reply, action }]);
        } catch (err) {
          setMessages(msgs => [...msgs, { from: 'ai', text: `Error: ${err.message}`, action }]);
        } finally {
          setQuestion('');
          setImageFile(null);
          setLoading(false);
        }
      };
      reader.readAsDataURL(imageFile);
      return;
    }

    // Non-image actions
    try {
      const res = await fetch('http://127.0.0.1:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(token && { Authorization: `Bearer ${token}` }) },
        body: JSON.stringify({ message: question, action })
      });
      const contentType = res.headers.get('content-type');
      let data;
      if (contentType && contentType.includes('application/json')) {
        data = await res.json();
      } else {
        const text = await res.text();
        throw new Error('Non-JSON response: ' + text);
      }
      setMessages(msgs => [...msgs, { from: 'ai', text: data.reply, action }]);
    } catch (err) {
      setMessages(msgs => [...msgs, { from: 'ai', text: `Error: ${err.message}`, action }]);
    } finally {
      setQuestion('');
      setImageFile(null);
      setLoading(false);
    }
  };

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
    <div style={{ maxWidth: 600, margin: '2rem auto', background: '#fff', borderRadius: 12, boxShadow: '0 2px 16px rgba(0,0,0,0.08)', padding: '2rem', height: '80vh', display: 'flex', flexDirection: 'column' }}>
      <h2>AI Tutor Chat</h2>
      <form onSubmit={sendMessage} style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <select value={action} onChange={e => setAction(e.target.value)} style={{ borderRadius: 6, padding: 6 }}>
            <option value="text">Text</option>
            <option value="code">Code</option>
            <option value="diagram">Diagram</option>
            <option value="quiz">Quiz</option>
            <option value="summarize">Summarize</option>
            <option value="image">Image</option>
          </select>

          <input
            value={action === 'image' ? '' : question}
            onChange={e => setQuestion(e.target.value)}
            placeholder={action === 'summarize' ? 'Enter YouTube URL...' : 'Ask a question...'}
            disabled={action === 'image'}
            style={{ borderRadius: 6, border: '1px solid #ccc', padding: 8, flex: 1 }}
            required={action !== 'image'}
          />
        </div>

        {action === 'image' && (
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setImageFile(e.target.files[0])}
            required
          />
        )}

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
