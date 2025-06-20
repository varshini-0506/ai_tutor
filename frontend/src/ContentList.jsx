import { useEffect, useState } from 'react';
import styles from './ContentList.module.css';

export default function ContentList({ token, role }) {
  const [content, setContent] = useState([]);
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/content')
      .then(res => res.json())
      .then(setContent);
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    setError('');
    const res = await fetch('http://127.0.0.1:5000/api/content', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ title, body })
    });
    if (res.ok) {
      const newItem = await res.json();
      setContent([...content, newItem]);
      setTitle('');
      setBody('');
    } else {
      const err = await res.json();
      setError(err.msg || 'Error adding content');
    }
  };

  return (
    <div className={styles.contentList}>
      <h2>Educational Content</h2>
      {role === 'teacher' && (
        <form className={styles.form} onSubmit={handleAdd}>
          <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Title" required />
          <input value={body} onChange={e => setBody(e.target.value)} placeholder="Body" required />
          <button type="submit">Add</button>
        </form>
      )}
      {error && <div style={{color: 'red', marginBottom: 10}}>{error}</div>}
      <div className={styles.cardGrid}>
        {content.map(item => (
          <div className={styles.card} key={item.id}>
            <h3>{item.title}</h3>
            <p>{item.body}</p>
          </div>
        ))}
      </div>
    </div>
  );
} 