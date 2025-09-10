import { useEffect, useState } from 'react';
import styles from './QuizList.module.css';

export default function QuizList({ token, role }) {
  const [quizzes, setQuizzes] = useState([]);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
          fetch('https://ai-tutor-backend-m4rr.onrender.com/api/quiz')
      .then(res => res.json())
      .then(setQuizzes);
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    setError('');
          const res = await fetch('https://ai-tutor-backend-m4rr.onrender.com/api/quiz', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ question, answer })
    });
    if (res.ok) {
      const newItem = await res.json();
      setQuizzes([...quizzes, newItem]);
      setQuestion('');
      setAnswer('');
    } else {
      const err = await res.json();
      setError(err.msg || 'Error adding quiz');
    }
  };

  return (
    <div className={styles.quizList}>
      <h2>Quizzes & Gamification</h2>
      {role === 'teacher' && (
        <form className={styles.form} onSubmit={handleAdd}>
          <input value={question} onChange={e => setQuestion(e.target.value)} placeholder="Question" required />
          <input value={answer} onChange={e => setAnswer(e.target.value)} placeholder="Answer" required />
          <button type="submit">Add Quiz</button>
        </form>
      )}
      {error && <div style={{color: 'red', marginBottom: 10}}>{error}</div>}
      <div className={styles.cardGrid}>
        {quizzes.map(item => (
          <div className={styles.card} key={item.id}>
            <h3>{item.question}</h3>
            <p><strong>Answer:</strong> {item.answer}</p>
          </div>
        ))}
      </div>
    </div>
  );
} 