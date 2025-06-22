import React, { useState, useEffect } from 'react';
import './Collaboration.css';
import TeamQuiz from './TeamQuiz';
import QuizTakingInterface from './QuizTakingInterface';

export default function Collaboration({ token, role }) {
  const [classrooms, setClassrooms] = useState([]);
  const [teamQuizzes, setTeamQuizzes] = useState([]);
  const [selectedClassroom, setSelectedClassroom] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [showCreateClassroom, setShowCreateClassroom] = useState(false);
  const [showCreateQuiz, setShowCreateQuiz] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [subjects, setSubjects] = useState([]);
  const [topics, setTopics] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [generatedQuestions, setGeneratedQuestions] = useState([]);
  const [isGeneratingQuiz, setIsGeneratingQuiz] = useState(false);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [showInteractiveQuiz, setShowInteractiveQuiz] = useState(false);
  const [showMemberManagement, setShowMemberManagement] = useState(false);
  const [selectedClassroomForMembers, setSelectedClassroomForMembers] = useState(null);
  const [newMemberUsername, setNewMemberUsername] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [classroomToDelete, setClassroomToDelete] = useState(null);
  const [showClassroomDetails, setShowClassroomDetails] = useState(false);
  const [selectedClassroomForDetails, setSelectedClassroomForDetails] = useState(null);

  // Form states
  const [classroomForm, setClassroomForm] = useState({
    name: '',
    description: '',
    subject: '',
    max_members: 20
  });

  const [quizForm, setQuizForm] = useState({
    classroom_id: '',
    time_limit: 30,
    team_mode: true,
    quiz_data: {
      title: '',
      questions: []
    }
  });

  const [newQuestion, setNewQuestion] = useState({
    question: '',
    options: ['', '', '', ''],
    correct_answer: 0
  });

  // Debug token on component mount
  useEffect(() => {
    console.log('Collaboration component mounted');
    console.log('Token received:', token);
    console.log('Token type:', typeof token);
    console.log('Token length:', token ? token.length : 'null');
    if (token) {
      console.log('Token starts with:', token.substring(0, 20) + '...');
    }
  }, [token]);

  // Test JWT token function
  const testJWT = async () => {
    try {
      console.log('Testing JWT token...');
      console.log('Token to test:', token);
      
      const response = await fetch('http://127.0.0.1:5000/api/test-jwt-main', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('JWT test response status:', response.status);
      const data = await response.json();
      console.log('JWT test response:', data);
      
      if (response.ok) {
        setSuccess('JWT token is working!');
      } else {
        setError(`JWT test failed: ${data.msg || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('JWT test error:', err);
      setError('JWT test failed');
    }
  };

  // Load data on component mount
  useEffect(() => {
    loadClassrooms();
    loadTeamQuizzes();
    loadSubjects();
  }, []);

  // Load messages when classroom is selected
  useEffect(() => {
    if (selectedClassroom) {
      loadMessages(selectedClassroom.id);
      const interval = setInterval(() => loadMessages(selectedClassroom.id), 3000);
      return () => clearInterval(interval);
    }
  }, [selectedClassroom]);

  const loadClassrooms = async () => {
    try {
      console.log('Loading classrooms...');
      console.log('Token:', token);
      
      // Check if token is expired
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          console.log('Token payload:', payload);
          console.log('Token expiration:', new Date(payload.exp * 1000));
          console.log('Current time:', new Date());
          console.log('Token is expired:', payload.exp * 1000 < Date.now());
          
          if (payload.exp * 1000 < Date.now()) {
            console.log('Token is expired!');
            setError('Token has expired. Please log in again.');
            return;
          }
        } catch (e) {
          console.log('Error parsing token:', e);
        }
      }
      
      const headers = { 'Authorization': `Bearer ${token}` };
      console.log('Request headers:', headers);
      
      const response = await fetch('http://127.0.0.1:5000/api/collaboration/classrooms', {
        headers: headers
      });
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Loaded classrooms:', data);
        console.log('Number of classrooms:', data.length);
        if (data.length > 0) {
          console.log('First classroom structure:', data[0]);
          console.log('First classroom created_by:', data[0].created_by);
          console.log('Current username from localStorage:', localStorage.getItem('username'));
        }
        setClassrooms(data);
      } else {
        const errorData = await response.json();
        console.log('Error response:', errorData);
        setError(errorData.msg || 'Failed to load classrooms');
      }
    } catch (err) {
      console.error('Exception:', err);
      setError('Failed to load classrooms');
    }
  };

  const loadTeamQuizzes = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/collaboration/team-quizzes', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setTeamQuizzes(data);
      }
    } catch (err) {
      setError('Failed to load team quizzes');
    }
  };

  const loadMessages = async (classroomId) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/collaboration/classrooms/${classroomId}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };

  const createClassroom = async (e) => {
    e.preventDefault();
    try {
      console.log('Creating classroom with data:', classroomForm);
      console.log('Token:', token);
      
      // Check if token is expired
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          console.log('Token payload:', payload);
          console.log('Token expiration:', new Date(payload.exp * 1000));
          console.log('Current time:', new Date());
          console.log('Token is expired:', payload.exp * 1000 < Date.now());
          
          if (payload.exp * 1000 < Date.now()) {
            console.log('Token is expired!');
            setError('Token has expired. Please log in again.');
            return;
          }
        } catch (e) {
          console.log('Error parsing token:', e);
        }
      }
      
      const response = await fetch('http://127.0.0.1:5000/api/collaboration/classrooms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(classroomForm)
      });
      
      console.log('Response status:', response.status);
      
      if (response.ok) {
        const newClassroom = await response.json();
        setClassrooms([...classrooms, newClassroom]);
        setShowCreateClassroom(false);
        setClassroomForm({ name: '', description: '', subject: '', max_members: 20 });
        setSuccess('Classroom created successfully!');
      } else {
        const error = await response.json();
        console.log('Error response:', error);
        setError(error.msg || 'Failed to create classroom');
      }
    } catch (err) {
      console.error('Exception:', err);
      setError('Failed to create classroom');
    }
  };

  const joinClassroom = async (classroomId) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/collaboration/classrooms/${classroomId}/join`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        await loadClassrooms();
        setSuccess('Successfully joined classroom!');
      } else {
        const error = await response.json();
        setError(error.error || 'Failed to join classroom');
      }
    } catch (err) {
      setError('Failed to join classroom');
    }
  };

  const leaveClassroom = async (classroomId) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/collaboration/classrooms/${classroomId}/leave`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        await loadClassrooms();
        if (selectedClassroom && selectedClassroom.id === classroomId) {
          setSelectedClassroom(null);
        }
        setSuccess('Successfully left classroom!');
      } else {
        const error = await response.json();
        setError(error.error || 'Failed to leave classroom');
      }
    } catch (err) {
      setError('Failed to leave classroom');
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedClassroom) return;

    try {
      const response = await fetch(`http://127.0.0.1:5000/api/collaboration/classrooms/${selectedClassroom.id}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: newMessage })
      });
      if (response.ok) {
        setNewMessage('');
        await loadMessages(selectedClassroom.id);
      }
    } catch (err) {
      setError('Failed to send message');
    }
  };

  const takeQuiz = (quiz) => {
    setSelectedQuiz(quiz);
    setShowInteractiveQuiz(true);
    loadTeamQuizzes(); // Refresh quiz list
  };

  const closeInteractiveQuiz = () => {
    setShowInteractiveQuiz(false);
    setSelectedQuiz(null);
    loadTeamQuizzes(); // Refresh quiz list
  };

  const joinTeamQuiz = async (quizId) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/collaboration/team-quizzes/${quizId}/join`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        await loadTeamQuizzes();
        setSuccess('Successfully joined team quiz!');
      } else {
        const error = await response.json();
        setError(error.error || 'Failed to join team quiz');
      }
    } catch (err) {
      setError('Failed to join team quiz');
    }
  };

  const startTeamQuiz = async (quizId) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/collaboration/team-quizzes/${quizId}/start`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        await loadTeamQuizzes();
        setSuccess('Team quiz started!');
      } else {
        const error = await response.json();
        setError(error.error || 'Failed to start team quiz');
      }
    } catch (err) {
      setError('Failed to start team quiz');
    }
  };

  const addQuestionToQuiz = () => {
    if (newQuestion.question && newQuestion.options.every(opt => opt.trim())) {
      setQuizForm({
        ...quizForm,
        quiz_data: {
          ...quizForm.quiz_data,
          questions: [...quizForm.quiz_data.questions, { ...newQuestion }]
        }
      });
      setNewQuestion({ question: '', options: ['', '', '', ''], correct_answer: 0 });
    }
  };

  const createTeamQuiz = async (e) => {
    e.preventDefault();
    if (quizForm.quiz_data.questions.length === 0) {
      setError('Please add at least one question');
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:5000/api/collaboration/team-quizzes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(quizForm)
      });
      if (response.ok) {
        const newQuiz = await response.json();
        setTeamQuizzes([...teamQuizzes, newQuiz]);
        setShowCreateQuiz(false);
        setQuizForm({
          classroom_id: '',
          time_limit: 30,
          team_mode: true,
          quiz_data: { title: '', questions: [] }
        });
        setSelectedSubject('');
        setTopics([]);
        setGeneratedQuestions([]);
        setSuccess('Team quiz created successfully!');
      } else {
        const error = await response.json();
        setError(error.error || 'Failed to create team quiz');
      }
    } catch (err) {
      setError('Failed to create team quiz');
    }
  };

  const loadSubjects = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/subjects');
      if (response.ok) {
        const data = await response.json();
        setSubjects(data);
      }
    } catch (err) {
      console.error('Failed to load subjects:', err);
    }
  };

  const loadTopics = async (subject) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/topics/${encodeURIComponent(subject)}`);
      if (response.ok) {
        const data = await response.json();
        setTopics(data);
      }
    } catch (err) {
      console.error('Failed to load topics:', err);
    }
  };

  const generateQuizQuestions = async (subject) => {
    try {
      setIsGeneratingQuiz(true);
      setError('');
      
      const response = await fetch(`http://127.0.0.1:5000/api/generate-quiz/${encodeURIComponent(subject)}`);
      const data = await response.json();
      
      if (response.ok && data.success) {
        setGeneratedQuestions(data.questions);
        // Auto-populate the quiz form with generated questions
        setQuizForm({
          ...quizForm,
          quiz_data: {
            ...quizForm.quiz_data,
            questions: data.questions
          }
        });
        
        if (data.note) {
          setSuccess(`${data.note}. Generated ${data.questions.length} quiz questions for ${subject}!`);
        } else {
          setSuccess(`Generated ${data.questions.length} quiz questions for ${subject}!`);
        }
      } else {
        setError(data.error || 'Failed to generate quiz questions');
      }
    } catch (err) {
      console.error('Failed to generate quiz questions:', err);
      setError('Failed to generate quiz questions');
    } finally {
      setIsGeneratingQuiz(false);
    }
  };

  const deleteClassroom = async (classroomId) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/collaboration/classrooms/${classroomId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        setClassrooms(classrooms.filter(c => c.id !== classroomId));
        setShowDeleteConfirm(false);
        setClassroomToDelete(null);
        setSuccess('Classroom deleted successfully!');
      } else {
        const error = await response.json();
        setError(error.error || 'Failed to delete classroom');
      }
    } catch (err) {
      setError('Failed to delete classroom');
    }
  };

  const addMember = async (classroomId, username) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/collaboration/classrooms/${classroomId}/members`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ username })
      });
      
      if (response.ok) {
        await loadClassrooms(); // Refresh classrooms to get updated member list
        setNewMemberUsername('');
        setSuccess(`Successfully added ${username} to the classroom!`);
      } else {
        const error = await response.json();
        setError(error.error || 'Failed to add member');
      }
    } catch (err) {
      setError('Failed to add member');
    }
  };

  const removeMember = async (classroomId, username) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/collaboration/classrooms/${classroomId}/members/${username}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        await loadClassrooms(); // Refresh classrooms to get updated member list
        setSuccess(`Successfully removed ${username} from the classroom!`);
      } else {
        const error = await response.json();
        setError(error.error || 'Failed to remove member');
      }
    } catch (err) {
      setError('Failed to remove member');
    }
  };

  const isClassroomOwner = (classroom) => {
    const currentUsername = localStorage.getItem('username');
    const classroomCreator = classroom.created_by;
    
    // Convert both to strings for comparison to handle any data type issues
    const usernameStr = String(currentUsername || '').trim();
    const creatorStr = String(classroomCreator || '').trim();
    
    const isOwner = usernameStr === creatorStr;
    
    console.log('Checking ownership for:', classroom.name);
    console.log('  - Classroom creator:', creatorStr);
    console.log('  - Current username:', usernameStr);
    console.log('  - Is owner:', isOwner);
    
    return isOwner;
  };

  const viewClassroomDetails = (classroom) => {
    setSelectedClassroomForDetails(classroom);
    setShowClassroomDetails(true);
  };

  const generateShareLink = (classroom) => {
    // Generate a shareable link or code for the classroom
    const shareCode = `CLASSROOM-${classroom.id}-${classroom.name.replace(/\s+/g, '-').toUpperCase()}`;
    return shareCode;
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      setSuccess('Share code copied to clipboard!');
    }).catch(() => {
      setError('Failed to copy to clipboard');
    });
  };

  return (
    <div className="collaboration-container">
      <div className="collaboration-header">
        <h1>Collaboration Hub</h1>
        <div className="header-actions">
          <button onClick={testJWT} className="btn-secondary">
            Test JWT
          </button>
          <button onClick={() => setShowCreateClassroom(true)} className="btn-primary">
            Create Classroom
          </button>
          <button onClick={() => setShowCreateQuiz(true)} className="btn-secondary">
            Take Quiz
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="collaboration-content">
        {/* Classrooms Section */}
        <div className="classrooms-section">
          <h2>Classrooms</h2>
          <div className="classrooms-grid">
            {classrooms.map(classroom => (
              <div key={classroom.id} className="classroom-card">
                <h3>{classroom.name}</h3>
                <p className="classroom-subject">{classroom.subject}</p>
                <p className="classroom-description">{classroom.description}</p>
                <div className="classroom-meta">
                  <span>Members: {classroom.members.length}/{classroom.max_members}</span>
                  <span>Created by: {classroom.created_by}</span>
                </div>
                <div className="classroom-actions">
                  <button 
                    onClick={() => viewClassroomDetails(classroom)}
                    className="btn-secondary"
                  >
                    View Details
                  </button>
                  {classroom.members.includes(localStorage.getItem('username')) ? (
                    <>
                      <button 
                        onClick={() => setSelectedClassroom(classroom)}
                        className="btn-primary"
                      >
                        Enter
                      </button>
                      <button 
                        onClick={() => leaveClassroom(classroom.id)}
                        className="btn-danger"
                      >
                        Leave
                      </button>
                    </>
                  ) : (
                    <button 
                      onClick={() => joinClassroom(classroom.id)}
                      className="btn-primary"
                    >
                      Join
                    </button>
                  )}
                  
                  {/* Owner-only actions */}
                  {isClassroomOwner(classroom) && (
                    <div className="owner-actions">
                      <button 
                        onClick={() => {
                          setSelectedClassroomForMembers(classroom);
                          setShowMemberManagement(true);
                        }}
                        className="btn-secondary"
                      >
                        Manage Members
                      </button>
                      <button 
                        onClick={() => {
                          setClassroomToDelete(classroom);
                          setShowDeleteConfirm(true);
                        }}
                        className="btn-danger"
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Team Quizzes Section */}
        <div className="quizzes-section">
          <h2>Team Quizzes</h2>
          <div className="quizzes-grid">
            {teamQuizzes.map(quiz => (
              <div key={quiz.id} className="quiz-card">
                <h3>{quiz.quiz_data.title || 'Untitled Quiz'}</h3>
                <p>Classroom: {quiz.classroom_name}</p>
                <p>Status: {quiz.status}</p>
                <p>Participants: {quiz.participants.length}</p>
                <div className="quiz-actions">
                  {quiz.status === 'waiting' && (
                    <>
                      {quiz.participants.includes(localStorage.getItem('username')) ? (
                        <button 
                          onClick={() => startTeamQuiz(quiz.id)}
                          className="btn-primary"
                        >
                          Start Quiz
                        </button>
                      ) : (
                        <button 
                          onClick={() => joinTeamQuiz(quiz.id)}
                          className="btn-secondary"
                        >
                          Join Quiz
                        </button>
                      )}
                    </>
                  )}
                  {quiz.status === 'active' && (
                    <button 
                      onClick={() => takeQuiz(quiz)}
                      className="btn-primary"
                    >
                      Take Quiz
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Classroom Chat */}
        {selectedClassroom && (
          <div className="chat-section">
            <div className="chat-header">
              <h3>{selectedClassroom.name} - Chat</h3>
              <button onClick={() => setSelectedClassroom(null)} className="btn-close">×</button>
            </div>
            <div className="chat-messages">
              {messages.map(message => (
                <div key={message.id} className={`message ${message.sender === localStorage.getItem('username') ? 'own' : 'other'}`}>
                  <div className="message-header">
                    <span className="sender">{message.sender}</span>
                    <span className="timestamp">{new Date(message.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <div className="message-content">{message.message}</div>
                </div>
              ))}
            </div>
            <form onSubmit={sendMessage} className="chat-input">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your message..."
                className="message-input"
              />
              <button type="submit" className="btn-primary">Send</button>
            </form>
          </div>
        )}
      </div>

      {/* Create Classroom Modal */}
      {showCreateClassroom && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Create Classroom</h2>
            <form onSubmit={createClassroom}>
              <input
                type="text"
                placeholder="Classroom Name"
                value={classroomForm.name}
                onChange={(e) => setClassroomForm({...classroomForm, name: e.target.value})}
                required
              />
              <textarea
                placeholder="Description"
                value={classroomForm.description}
                onChange={(e) => setClassroomForm({...classroomForm, description: e.target.value})}
              />
              <select
                value={classroomForm.subject}
                onChange={(e) => setClassroomForm({...classroomForm, subject: e.target.value})}
                required
              >
                <option value="">Select Subject</option>
                {subjects.map(subject => (
                  <option key={subject} value={subject}>{subject}</option>
                ))}
              </select>
              <input
                type="number"
                placeholder="Max Members"
                value={classroomForm.max_members || ''}
                onChange={(e) => setClassroomForm({...classroomForm, max_members: parseInt(e.target.value) || 20})}
                min="2"
                max="50"
              />
              <div className="modal-actions">
                <button type="submit" className="btn-primary">Create</button>
                <button type="button" onClick={() => setShowCreateClassroom(false)} className="btn-secondary">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Take Quiz Modal */}
      {showCreateQuiz && (
        <div className="modal-overlay">
          <div className="modal large-modal">
            <h2>Take Quiz</h2>
            {!showInteractiveQuiz ? (
              <form onSubmit={(e) => {
                e.preventDefault();
                if (generatedQuestions.length > 0) {
                  setShowInteractiveQuiz(true);
                }
              }}>
                <select
                  value={quizForm.classroom_id}
                  onChange={(e) => setQuizForm({...quizForm, classroom_id: e.target.value})}
                  required
                >
                  <option value="">Select Classroom</option>
                  {classrooms.length > 0 ? (
                    classrooms.map(classroom => (
                      <option key={classroom.id} value={classroom.name}>
                        {classroom.name} ({classroom.members.length} members)
                      </option>
                    ))
                  ) : (
                    <option value="General">General Quiz (No specific classroom)</option>
                  )}
                </select>
                
                <select
                  value={selectedSubject}
                  onChange={(e) => {
                    setSelectedSubject(e.target.value);
                    if (e.target.value) {
                      loadTopics(e.target.value);
                      // Auto-generate quiz questions when subject is selected
                      generateQuizQuestions(e.target.value);
                    } else {
                      setTopics([]);
                      setGeneratedQuestions([]);
                    }
                  }}
                  required
                >
                  <option value="">Select Subject</option>
                  {subjects.map(subject => (
                    <option key={subject} value={subject}>{subject}</option>
                  ))}
                </select>
                
                {isGeneratingQuiz && (
                  <div className="loading-message">
                    <p>🤖 Generating quiz questions for {selectedSubject}...</p>
                  </div>
                )}
                
                {generatedQuestions.length > 0 && (
                  <div className="generated-questions">
                    <h4>Quiz Questions ({generatedQuestions.length})</h4>
                    <p>Ready to start the quiz!</p>
                  </div>
                )}
                
                <select
                  value={quizForm.quiz_data.title}
                  onChange={(e) => setQuizForm({
                    ...quizForm, 
                    quiz_data: {...quizForm.quiz_data, title: e.target.value}
                  })}
                  required
                >
                  <option value="">Select Topic</option>
                  {topics.map(topic => (
                    <option key={topic.title} value={topic.title}>{topic.title}</option>
                  ))}
                </select>
                
                <div className="modal-actions">
                  <button 
                    type="submit" 
                    className="btn-primary"
                    disabled={generatedQuestions.length === 0}
                  >
                    Start Quiz
                  </button>
                  <button type="button" onClick={() => setShowCreateQuiz(false)} className="btn-secondary">
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <div className="quiz-taking-interface">
                <QuizTakingInterface 
                  questions={generatedQuestions}
                  subject={selectedSubject}
                  title={quizForm.quiz_data.title}
                  onClose={() => {
                    setShowCreateQuiz(false);
                    setShowInteractiveQuiz(false);
                    setGeneratedQuestions([]);
                    setSelectedSubject('');
                    setQuizForm({
                      classroom_id: '',
                      time_limit: 30,
                      team_mode: true,
                      quiz_data: { title: '', questions: [] }
                    });
                  }}
                />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Interactive Quiz Modal */}
      {showInteractiveQuiz && selectedQuiz && (
        <TeamQuiz 
          quiz={selectedQuiz}
          onClose={closeInteractiveQuiz}
          token={token}
        />
      )}

      {/* Member Management Modal */}
      {showMemberManagement && selectedClassroomForMembers && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Manage Members - {selectedClassroomForMembers.name}</h2>
            <div className="member-management">
              <div className="current-members">
                <h3>Current Members ({selectedClassroomForMembers.members.length}/{selectedClassroomForMembers.max_members})</h3>
                <div className="members-list">
                  {selectedClassroomForMembers.members.map((member, index) => (
                    <div key={index} className="member-item">
                      <span className="member-name">{member}</span>
                      {member !== selectedClassroomForMembers.created_by && (
                        <button 
                          onClick={() => removeMember(selectedClassroomForMembers.id, member)}
                          className="btn-danger small"
                        >
                          Remove
                        </button>
                      )}
                      {member === selectedClassroomForMembers.created_by && (
                        <span className="owner-badge">Owner</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="add-member">
                <h3>Add New Member</h3>
                <div className="add-member-form">
                  <input
                    type="text"
                    placeholder="Enter username"
                    value={newMemberUsername}
                    onChange={(e) => setNewMemberUsername(e.target.value)}
                  />
                  <button 
                    onClick={() => addMember(selectedClassroomForMembers.id, newMemberUsername)}
                    className="btn-primary"
                    disabled={!newMemberUsername.trim()}
                  >
                    Add Member
                  </button>
                </div>
              </div>
            </div>
            
            <div className="modal-actions">
              <button 
                onClick={() => {
                  setShowMemberManagement(false);
                  setSelectedClassroomForMembers(null);
                  setNewMemberUsername('');
                }} 
                className="btn-secondary"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && classroomToDelete && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Delete Classroom</h2>
            <div className="delete-confirmation">
              <p>Are you sure you want to delete the classroom <strong>"{classroomToDelete.name}"</strong>?</p>
              <p>This action cannot be undone. All members will be removed and the classroom will be permanently deleted.</p>
            </div>
            
            <div className="modal-actions">
              <button 
                onClick={() => deleteClassroom(classroomToDelete.id)}
                className="btn-danger"
              >
                Delete Classroom
              </button>
              <button 
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setClassroomToDelete(null);
                }} 
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Classroom Details Modal */}
      {showClassroomDetails && selectedClassroomForDetails && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Classroom Details</h2>
            <div className="classroom-details">
              <div className="detail-section">
                <h3>{selectedClassroomForDetails.name}</h3>
                <p className="detail-subject">Subject: {selectedClassroomForDetails.subject}</p>
                <p className="detail-description">{selectedClassroomForDetails.description}</p>
              </div>
              
              <div className="detail-section">
                <h4>Classroom Information</h4>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="info-label">Created by:</span>
                    <span className="info-value">{selectedClassroomForDetails.created_by}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Members:</span>
                    <span className="info-value">{selectedClassroomForDetails.members.length}/{selectedClassroomForDetails.max_members}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Status:</span>
                    <span className="info-value">
                      {selectedClassroomForDetails.members.includes(localStorage.getItem('username')) ? 'Member' : 'Not a member'}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="detail-section">
                <h4>Current Members</h4>
                <div className="members-preview">
                  {selectedClassroomForDetails.members.map((member, index) => (
                    <span key={index} className="member-tag">
                      {member}
                      {member === selectedClassroomForDetails.created_by && <span className="owner-indicator">👑</span>}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="detail-section">
                <h4>Share Classroom</h4>
                <p>Share this code with others to let them join your classroom:</p>
                <div className="share-code">
                  <input
                    type="text"
                    value={generateShareLink(selectedClassroomForDetails)}
                    readOnly
                    className="share-input"
                  />
                  <button 
                    onClick={() => copyToClipboard(generateShareLink(selectedClassroomForDetails))}
                    className="btn-primary"
                  >
                    Copy Code
                  </button>
                </div>
                <p className="share-instructions">
                  Others can use this code to join your classroom. Simply share this code with them!
                </p>
              </div>
            </div>
            
            <div className="modal-actions">
              {!selectedClassroomForDetails.members.includes(localStorage.getItem('username')) && (
                <button 
                  onClick={() => joinClassroom(selectedClassroomForDetails.id)}
                  className="btn-primary"
                >
                  Join Classroom
                </button>
              )}
              <button 
                onClick={() => {
                  setShowClassroomDetails(false);
                  setSelectedClassroomForDetails(null);
                }} 
                className="btn-secondary"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 