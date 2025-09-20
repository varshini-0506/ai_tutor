import React, { useState, useEffect } from 'react';
import './Quiz.css';

export default function Quiz({ token }) {
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [isGeneratingQuiz, setIsGeneratingQuiz] = useState(false);
  const [showQuiz, setShowQuiz] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Quiz state
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [score, setScore] = useState(0);
  const [answeredQuestions, setAnsweredQuestions] = useState(new Set());
  const [timeLeft, setTimeLeft] = useState(30);
  const [quizCompleted, setQuizCompleted] = useState(false);

  useEffect(() => {
    loadSubjects();
  }, []);

  useEffect(() => {
    if (showQuiz && timeLeft > 0 && !quizCompleted) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && !quizCompleted) {
      handleNextQuestion();
    }
  }, [timeLeft, quizCompleted, showQuiz]);

  const loadSubjects = async () => {
    try {
      const response = await fetch('https://ai-tutor-backend-m4rr.onrender.com/api/subjects');
      if (response.ok) {
        const data = await response.json();
        setSubjects(data);
      }
    } catch (err) {
      console.error('Failed to load subjects:', err);
    }
  };

  const generateQuiz = async (subject) => {
    try {
      setIsGeneratingQuiz(true);
      setError('');
      
              const response = await fetch(`https://ai-tutor-backend-m4rr.onrender.com/api/generate-quiz/${encodeURIComponent(subject)}`);
      const data = await response.json();
      
      if (response.ok && data.success) {
        setQuizQuestions(data.questions);
        setShowQuiz(true);
        setSuccess(`Generated ${data.questions.length} quiz questions for ${subject}!`);
        
        // Reset quiz state
        setCurrentQuestionIndex(0);
        setSelectedAnswer(null);
        setShowFeedback(false);
        setScore(0);
        setAnsweredQuestions(new Set());
        setTimeLeft(30);
        setQuizCompleted(false);
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

  const handleAnswerSelect = (answerIndex) => {
    if (answeredQuestions.has(currentQuestionIndex)) return;
    
    setSelectedAnswer(answerIndex);
    setShowFeedback(true);
    
    const currentQuestion = quizQuestions[currentQuestionIndex];
    const isCorrect = answerIndex === currentQuestion.correct_answer;
    
    if (isCorrect) {
      setScore(score + 1);
    }
    
    setAnsweredQuestions(prev => new Set([...prev, currentQuestionIndex]));
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < quizQuestions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setSelectedAnswer(null);
      setShowFeedback(false);
      setTimeLeft(30);
    } else {
      setQuizCompleted(true);
    }
  };

  const handleFinishQuiz = () => {
    setShowQuiz(false);
    setQuizQuestions([]);
    setSelectedSubject('');
    setSuccess(`Quiz completed! Your score: ${score}/${quizQuestions.length} (${Math.round((score / quizQuestions.length) * 100)}%)`);
  };

  const handleStartNewQuiz = () => {
    setShowQuiz(false);
    setQuizQuestions([]);
    setSelectedSubject('');
    setError('');
    setSuccess('');
  };

  if (showQuiz && quizQuestions.length > 0) {
    if (quizCompleted) {
      return (
        <div className="quiz-overlay">
          <div className="quiz-modal">
            <h2>Quiz Completed! 🎉</h2>
            <div className="quiz-results">
              <div className="score-display">
                <h3>Your Score</h3>
                <div className="score-circle">
                  <span className="score-number">{score}</span>
                  <span className="score-total">/ {quizQuestions.length}</span>
                </div>
                <p className="score-percentage">
                  {Math.round((score / quizQuestions.length) * 100)}%
                </p>
              </div>
              <div className="score-message">
                {score === quizQuestions.length && <p>Perfect! Excellent work! 🌟</p>}
                {score >= quizQuestions.length * 0.8 && score < quizQuestions.length && <p>Great job! Well done! 👍</p>}
                {score >= quizQuestions.length * 0.6 && score < quizQuestions.length * 0.8 && <p>Good effort! Keep practicing! 💪</p>}
                {score < quizQuestions.length * 0.6 && <p>Keep studying! You'll improve! 📚</p>}
              </div>
            </div>
            <div className="quiz-actions">
              <button onClick={handleFinishQuiz} className="btn-primary">Finish Quiz</button>
              <button onClick={handleStartNewQuiz} className="btn-secondary">Take Another Quiz</button>
            </div>
          </div>
        </div>
      );
    }

    const currentQuestion = quizQuestions[currentQuestionIndex];

    return (
      <div className="quiz-overlay">
        <div className="quiz-modal">
          <div className="quiz-header">
            <h2>{selectedSubject} Quiz</h2>
            <div className="quiz-info">
              <span className="question-counter">
                Question {currentQuestionIndex + 1} of {quizQuestions.length}
              </span>
              <span className="timer">
                Time: {timeLeft}s
              </span>
              <span className="score">
                Score: {score}/{quizQuestions.length}
              </span>
            </div>
          </div>

          <div className="question-container">
            <h3 className="question-text">{currentQuestion.question}</h3>
            
            <div className="options-container">
              {currentQuestion.options.map((option, index) => {
                let optionClass = 'option';
                let isSelected = selectedAnswer === index;
                let isCorrect = index === currentQuestion.correct_answer;
                
                if (showFeedback) {
                  if (isCorrect) {
                    optionClass += ' correct';
                  } else if (isSelected && !isCorrect) {
                    optionClass += ' incorrect';
                  }
                } else if (isSelected) {
                  optionClass += ' selected';
                }

                return (
                  <button
                    key={index}
                    className={optionClass}
                    onClick={() => handleAnswerSelect(index)}
                    disabled={answeredQuestions.has(currentQuestionIndex)}
                  >
                    <span className="option-letter">{String.fromCharCode(65 + index)}.</span>
                    <span className="option-text">{option}</span>
                    {showFeedback && isCorrect && <span className="correct-icon">✓</span>}
                    {showFeedback && isSelected && !isCorrect && <span className="incorrect-icon">✗</span>}
                  </button>
                );
              })}
            </div>

            {showFeedback && (
              <div className="feedback-container">
                {selectedAnswer === currentQuestion.correct_answer ? (
                  <div className="feedback correct-feedback">
                    <span className="feedback-icon">🎉</span>
                    <p>Correct! Well done!</p>
                  </div>
                ) : (
                  <div className="feedback incorrect-feedback">
                    <span className="feedback-icon">❌</span>
                    <p>Incorrect. The correct answer is: <strong>{currentQuestion.options[currentQuestion.correct_answer]}</strong></p>
                  </div>
                )}
                {currentQuestion.explanation && (
                  <div className="explanation">
                    <p><strong>Explanation:</strong> {currentQuestion.explanation}</p>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="quiz-actions">
            {showFeedback && (
              <button onClick={handleNextQuestion} className="btn-primary">
                {currentQuestionIndex < quizQuestions.length - 1 ? 'Next Question' : 'Finish Quiz'}
              </button>
            )}
            <button onClick={handleStartNewQuiz} className="btn-secondary">Exit Quiz</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="quiz-container">
      <div className="quiz-header">
        <h1>Take Quiz</h1>
        <p>Test your knowledge with interactive quizzes on various subjects!</p>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="subjects-grid">
        {subjects.map(subject => (
          <div key={subject} className="subject-card">
            <h3>{subject}</h3>
            <p>Test your knowledge in {subject}</p>
            <button 
              onClick={() => {
                setSelectedSubject(subject);
                generateQuiz(subject);
              }}
              className="btn-primary"
              disabled={isGeneratingQuiz}
            >
              {isGeneratingQuiz && selectedSubject === subject ? 'Generating Quiz...' : 'Take Quiz'}
            </button>
          </div>
        ))}
      </div>

      {isGeneratingQuiz && (
        <div className="loading-overlay">
          <div className="loading-content">
            <div className="spinner"></div>
            <p>Generating quiz questions for {selectedSubject}...</p>
          </div>
        </div>
      )}
    </div>
  );
} 