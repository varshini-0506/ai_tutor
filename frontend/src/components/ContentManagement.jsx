import React, { useState, useEffect } from 'react';
import './ContentManagement.css';

export default function ContentManagement() {
  const [content, setContent] = useState([]);
  const [activeSubject, setActiveSubject] = useState(null);
  const [showAddForm, setShowAddForm] = useState(null);
  const [newTopic, setNewTopic] = useState({ title: '', videoUrl: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch course data from backend
  const fetchCourseData = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch('http://localhost:5000/api/course-data');
      if (!res.ok) throw new Error('Failed to fetch course data');
      const data = await res.json();
      setContent(data);
    } catch (e) {
      setError('Could not load course data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCourseData();
  // eslint-disable-next-line
  }, []);

  const handleAddTopic = async (subjectIndex) => {
    if (!newTopic.title || !newTopic.videoUrl) {
      alert("Please provide both a title and a video URL.");
      return;
    }
    setError('');
    try {
      const subject = content[subjectIndex].subject;
      const res = await fetch('http://localhost:5000/api/course-data/add-topic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject, title: newTopic.title, videoUrl: newTopic.videoUrl })
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Failed to add topic');
      setContent(data.data);
      setNewTopic({ title: '', videoUrl: '' });
      setShowAddForm(null);
    } catch (e) {
      setError('Could not add topic.');
    }
  };

  const handleDeleteTopic = async (subjectIndex, topicIndex) => {
    if (!window.confirm("Are you sure you want to delete this topic?")) return;
    setError('');
    try {
      const subject = content[subjectIndex].subject;
      const title = content[subjectIndex].topics[topicIndex].title;
      const res = await fetch('http://localhost:5000/api/course-data/delete-topic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject, title })
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Failed to delete topic');
      setContent(data.data);
    } catch (e) {
      setError('Could not delete topic.');
    }
  };

  const toggleSubject = (index) => {
    setActiveSubject(activeSubject === index ? null : index);
    setShowAddForm(null);
  };

  return (
    <div className="content-management-container">
      <h2>Course Content Management</h2>
      {error && <div className="error-message">{error}</div>}
      {loading ? (
        <div>Loading...</div>
      ) : (
        <div className="accordion">
          {content.map((subject, subjectIndex) => (
            <div key={subjectIndex} className={`accordion-item${activeSubject === subjectIndex ? ' open' : ''}`}>
              <button
                className="accordion-header"
                onClick={() => toggleSubject(subjectIndex)}
              >
                <span>{subject.subject}</span>
                <span className={`accordion-icon${activeSubject === subjectIndex ? ' open' : ''}`}>
                  &#9660;
                </span>
              </button>
              {activeSubject === subjectIndex && (
                <div className="accordion-content">
                  <div className="topic-list">
                    {subject.topics.map((topic, topicIndex) => (
                      <div key={topicIndex} className="topic-chip">
                        <span>🎬 {topic.title}</span>
                        <button
                          className="chip-delete"
                          title="Delete Topic"
                          onClick={() => handleDeleteTopic(subjectIndex, topicIndex)}
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                  {showAddForm === subjectIndex ? (
                    <form className="add-topic-form" onSubmit={e => { e.preventDefault(); handleAddTopic(subjectIndex); }}>
                      <input
                        type="text"
                        placeholder="Topic Title"
                        value={newTopic.title}
                        onChange={e => setNewTopic({ ...newTopic, title: e.target.value })}
                        required
                      />
                      <input
                        type="text"
                        placeholder="YouTube Video URL"
                        value={newTopic.videoUrl}
                        onChange={e => setNewTopic({ ...newTopic, videoUrl: e.target.value })}
                        required
                      />
                      <button type="submit" title="Add Topic">＋ Add</button>
                    </form>
                  ) : (
                    <button className="add-topic-fab" onClick={() => setShowAddForm(subjectIndex)}>
                      ＋ Add Topic
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 