import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './AiTutorChat.css';

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

// Voice Recognition Component
function VoiceRecognition({ onTranscript, isListening, setIsListening }) {
  const recognitionRef = useRef(null);
  const isInitialized = useRef(false);
  const [browserSupport, setBrowserSupport] = useState(null);

  useEffect(() => {
    // Check browser support and HTTPS
    const checkBrowserSupport = () => {
      // Check if running on HTTPS or localhost
      const isSecure = window.location.protocol === 'https:' || 
                      window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1';
      
      if (!isSecure) {
        console.warn('Speech recognition requires HTTPS or localhost');
        setBrowserSupport('insecure');
        return false;
      }

      if ('webkitSpeechRecognition' in window) {
        setBrowserSupport('webkit');
        return true;
      } else if ('SpeechRecognition' in window) {
        setBrowserSupport('standard');
        return true;
      } else {
        setBrowserSupport('none');
        return false;
      }
    };

    // Initialize speech recognition only once
    if (!isInitialized.current && checkBrowserSupport()) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      try {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;
        recognitionRef.current.lang = 'en-US';
        recognitionRef.current.maxAlternatives = 1;
        
        // Add timeout to prevent hanging
        recognitionRef.current.timeout = 10000; // 10 seconds
        recognitionRef.current.grammars = null;

        recognitionRef.current.onresult = (event) => {
          console.log('Speech recognition result received');
          let finalTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            }
          }
          if (finalTranscript) {
            console.log('Final transcript:', finalTranscript);
            onTranscript(finalTranscript);
            setIsListening(false);
          }
        };

        recognitionRef.current.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          
          // Handle specific error types
          switch (event.error) {
            case 'aborted':
              console.log('Speech recognition was aborted - this is normal when stopping');
              break;
            case 'audio-capture':
              console.log('No microphone was found');
              alert('🎤 No microphone detected. Please check your microphone connection and try again.');
              break;
            case 'bad-grammar':
              console.log('Speech recognition grammar error');
              alert('⚠️ Speech recognition grammar error. Please try again.');
              break;
            case 'language-not-supported':
              console.log('Language not supported');
              alert('🌍 Language not supported. Please try again.');
              break;
            case 'network':
              console.log('Network error occurred');
              alert('🌐 Network error occurred. Please check your internet connection and try again. Voice recognition requires an internet connection.');
              break;
            case 'no-speech':
              console.log('No speech was detected');
              alert('🔇 No speech detected. Please speak more clearly and try again.');
              break;
            case 'not-allowed':
              console.log('Permission denied for microphone');
              alert('🚫 Microphone permission denied. Please allow microphone access in your browser settings and refresh the page.');
              break;
            case 'service-not-allowed':
              console.log('Speech recognition service not allowed');
              alert('🚫 Speech recognition service not allowed. Please check your browser settings.');
              break;
            default:
              console.log('Unknown speech recognition error:', event.error);
              alert(`❌ Speech recognition error: ${event.error}. Please try again.`);
          }
          
          setIsListening(false);
        };

        recognitionRef.current.onend = () => {
          console.log('Speech recognition ended');
          setIsListening(false);
        };

        recognitionRef.current.onstart = () => {
          console.log('Speech recognition started');
        };

        isInitialized.current = true;
        console.log('Speech recognition initialized successfully');
      } catch (error) {
        console.error('Error initializing speech recognition:', error);
        setBrowserSupport('error');
      }
    }

    // Cleanup function
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (error) {
          console.log('Error stopping recognition during cleanup:', error);
        }
      }
    };
  }, [onTranscript, setIsListening]);

  const startListening = () => {
    if (!recognitionRef.current) {
      alert('🚫 Voice recognition is not supported in your browser or requires HTTPS.');
      return;
    }
    
    if (isListening) {
      console.log('Already listening');
      return;
    }
    
    try {
      console.log('Starting speech recognition...');
      
      // Stop any existing recognition first
      try {
        recognitionRef.current.stop();
      } catch (e) {
        // Ignore errors when stopping
      }
      
      // Small delay to ensure clean restart
      setTimeout(() => {
        try {
          recognitionRef.current.start();
          setIsListening(true);
          console.log('Speech recognition started successfully');
        } catch (error) {
          console.error('Error starting speech recognition:', error);
          setIsListening(false);
          
          // Provide specific error messages
          if (error.name === 'NotAllowedError') {
            alert('🚫 Microphone permission denied. Please allow microphone access and refresh the page.');
          } else if (error.name === 'NotFoundError') {
            alert('🎤 No microphone found. Please check your microphone connection.');
          } else {
            alert('❌ Failed to start voice recognition. Please try again.');
          }
        }
      }, 200); // Increased delay for better reliability
    } catch (error) {
      console.error('Error in startListening:', error);
      setIsListening(false);
      alert('❌ Failed to start voice recognition. Please try again.');
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      try {
        console.log('Stopping speech recognition...');
        recognitionRef.current.stop();
        setIsListening(false);
      } catch (error) {
        console.error('Error stopping speech recognition:', error);
        setIsListening(false);
      }
    }
  };

  // Show different states based on browser support
  if (browserSupport === 'none') {
    return (
      <div className="voice-status">
        <button className="voice-btn disabled" disabled>
          🎤 Voice not supported
        </button>
        <p className="voice-help">Use Chrome or Edge browser for voice support</p>
      </div>
    );
  }

  if (browserSupport === 'error') {
    return (
      <div className="voice-status">
        <button className="voice-btn disabled" disabled>
          🎤 Voice error
        </button>
        <p className="voice-help">Voice recognition failed to initialize</p>
      </div>
    );
  }

  if (!isInitialized.current) {
    return (
      <div className="voice-status">
        <button className="voice-btn disabled" disabled>
          🎤 Initializing...
        </button>
      </div>
    );
  }

  // Show browser support status
  const getBrowserSupportMessage = () => {
    switch (browserSupport) {
      case 'insecure':
        return '🚫 Voice recognition requires HTTPS or localhost';
      case 'webkit':
        return '✅ Voice recognition supported (WebKit)';
      case 'standard':
        return '✅ Voice recognition supported';
      case 'none':
        return '❌ Voice recognition not supported in this browser';
      default:
        return '⏳ Checking voice recognition support...';
    }
  };

  return (
    <div className="voice-status">
      <div className="browser-support-status" style={{ 
        marginBottom: '1rem', 
        padding: '0.5rem', 
        borderRadius: '8px',
        backgroundColor: browserSupport === 'webkit' || browserSupport === 'standard' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
        color: browserSupport === 'webkit' || browserSupport === 'standard' ? '#059669' : '#dc2626',
        fontSize: '0.9rem',
        textAlign: 'center',
        border: `1px solid ${browserSupport === 'webkit' || browserSupport === 'standard' ? '#34d399' : '#f87171'}`
      }}>
        {getBrowserSupportMessage()}
      </div>
      
      <button
        className={`voice-btn ${isListening ? 'listening' : ''}`}
        onClick={isListening ? stopListening : startListening}
        title={isListening ? 'Stop listening' : 'Start voice input'}
        disabled={!recognitionRef.current || browserSupport === 'none' || browserSupport === 'insecure'}
      >
        {isListening ? '🔴 Stop' : '🎤 Voice'}
      </button>
      {isListening && (
        <p className="voice-instructions">
          Speak now... Click stop when finished
        </p>
      )}
    </div>
  );
}

export default function AiTutorChat({ token }) {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [action, setAction] = useState('text');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [showVoiceButton, setShowVoiceButton] = useState(false);
  const [ocrStatus, setOcrStatus] = useState(null);

  // Check OCR status on component mount
  useEffect(() => {
    const checkOcrStatus = async () => {
      try {
        const res = await fetch('https://ai-tutor-backend-m4rr.onrender.com/check-ocr');
        const data = await res.json();
        setOcrStatus(data);
        if (!data.available) {
          console.warn('OCR not available:', data.message);
        }
      } catch (error) {
        console.error('Error checking OCR status:', error);
        setOcrStatus({ available: false, message: 'Could not check OCR status' });
      }
    };
    
    checkOcrStatus();
  }, []);

  // Handle voice transcript
  const handleVoiceTranscript = (transcript) => {
    setQuestion(transcript);
    setShowVoiceButton(false);
  };

  // Handle image file selection
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      // Create preview URL
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  // Clear image
  const clearImage = () => {
    setImageFile(null);
    setImagePreview(null);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!question && action !== 'image') return;
    if (action === 'image' && !imageFile) return;
    
    setLoading(true);
    setMessages([...messages, { from: 'user', text: question || 'Image uploaded', action }]);

    // Handle image upload
    if (action === 'image' && imageFile) {
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64String = reader.result;
        try {
          // Use the dedicated analyze-image route for better OCR processing
          const res = await fetch('https://ai-tutor-backend-m4rr.onrender.com/analyze-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...(token && { Authorization: `Bearer ${token}` }) },
            body: JSON.stringify({ 
              image: base64String, 
              analysis_type: 'educational' 
            })
          });
          
          if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
          }
          
          const contentType = res.headers.get('content-type');
          let data;
          if (contentType && contentType.includes('application/json')) {
            data = await res.json();
          } else {
            const text = await res.text();
            throw new Error('Non-JSON response: ' + text);
          }
          
          if (data.error) {
            throw new Error(data.error);
          }
          
          setMessages(msgs => [...msgs, { from: 'ai', text: data.analysis, action }]);
        } catch (err) {
          console.error('Image processing error:', err);
          setMessages(msgs => [...msgs, { from: 'ai', text: `Error processing image: ${err.message}`, action }]);
        } finally {
          setQuestion('');
          setImageFile(null);
          setImagePreview(null);
          setLoading(false);
        }
      };
      reader.readAsDataURL(imageFile);
      return;
    }

    // Handle text-based actions
    try {
      const res = await fetch('https://ai-tutor-backend-m4rr.onrender.com/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(token && { Authorization: `Bearer ${token}` }) },
        body: JSON.stringify({ message: question, action })
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
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
      console.error('Chat error:', err);
      setMessages(msgs => [...msgs, { from: 'ai', text: `Error: ${err.message}`, action }]);
    } finally {
      setQuestion('');
      setImageFile(null);
      setImagePreview(null);
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
    <div className="ai-tutor-container">
      <div className="ai-tutor-header">
        <h2>🤖 AI Tutor</h2>
        <div className="header-controls">
          {ocrStatus && (
            <span 
              className={`ocr-status ${ocrStatus.available ? 'available' : 'unavailable'}`}
              title={ocrStatus.message}
            >
              📷 {ocrStatus.available ? 'OCR Ready' : 'OCR Unavailable'}
            </span>
          )}
          <button 
            className="voice-toggle-btn"
            onClick={() => setShowVoiceButton(!showVoiceButton)}
            title="Toggle voice input"
          >
            🎤 Voice Input
          </button>
        </div>
      </div>

      {showVoiceButton && (
        <div className="voice-section">
          <VoiceRecognition 
            onTranscript={handleVoiceTranscript}
            isListening={isListening}
            setIsListening={setIsListening}
          />
          <p className="voice-instructions">
            Click the voice button to start speaking. Your speech will be converted to text automatically.
          </p>
        </div>
      )}

      <form onSubmit={sendMessage} className="chat-form">
        <div className="input-group">
          <select value={action} onChange={e => setAction(e.target.value)} className="action-select">
            <option value="text">💬 Text</option>
            <option value="code">💻 Code</option>
            <option value="diagram">📊 Diagram</option>
            <option value="quiz">❓ Quiz</option>
            <option value="summarize">📝 Summarize</option>
            <option value="image">🖼️ Image</option>
          </select>

          <input
            value={action === 'image' ? '' : question}
            onChange={e => setQuestion(e.target.value)}
            placeholder={action === 'summarize' ? 'Enter YouTube URL...' : 'Ask a question...'}
            disabled={action === 'image'}
            className="question-input"
            required={action !== 'image'}
          />

          <button type="submit" disabled={loading || (action === 'image' && !imageFile)} className="send-btn">
            {loading ? '🔄 Thinking...' : '🚀 Send'}
          </button>
        </div>

        {action === 'image' && (
          <div className="image-upload-section">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              required
              className="file-input"
            />
            {imagePreview && (
              <div className="image-preview-container">
                <img src={imagePreview} alt="Preview" className="image-preview" />
                <button 
                  type="button" 
                  onClick={clearImage}
                  className="clear-image-btn"
                >
                  ❌ Clear
                </button>
              </div>
            )}
          </div>
        )}
      </form>

      <div className="messages-container">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.from === 'ai' ? 'ai' : 'user'}`}>
            <div className="message-header">
              <strong>{msg.from === 'ai' ? '🤖 AI' : '👤 You'}</strong>
              {msg.action && <span className="action-tag">{msg.action}</span>}
            </div>
            <div className="message-content">
              {msg.from === 'ai' && msg.action === 'quiz' ? (
                <QuizMessage text={msg.text} />
              ) : msg.from === 'ai' ? (
                <MarkdownWithCode>{msg.text}</MarkdownWithCode>
              ) : (
                msg.text
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
