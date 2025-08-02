import { useAuth } from './AuthContext.jsx';

export default function Home() {
  const { user } = useAuth();
  const isTeacher = user?.role === 'teacher';

  if (isTeacher) {
    return (
      <div className="home">
        <h1>Welcome, Teacher!</h1>
        <p>Manage your classes, students, and educational content from your dashboard.</p>
        <div className="teacher-dashboard">
          <div className="dashboard-grid">
            <div className="dashboard-card">
              <h3>Quick Actions</h3>
              <ul>
                <li>Create a new lesson</li>
                <li>Assign a quiz</li>
                <li>View student progress</li>
                <li>Generate reports</li>
              </ul>
            </div>
            <div className="dashboard-card">
              <h3>Recent Activity</h3>
              <p>No recent activity to display</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="home">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Welcome to AI Tutor</h1>
          <p className="hero-subtitle">Your intelligent learning companion designed to enhance your educational journey</p>
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-number">5+</span>
              <span className="stat-label">Subjects</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">50+</span>
              <span className="stat-label">Topics</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">24/7</span>
              <span className="stat-label">AI Support</span>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="features-section">
        <h2 className="section-title">Discover Our Features</h2>
        <div className="features-grid">
          
          {/* Educational Content */}
          <div className="feature-card">
            <div className="feature-icon">📚</div>
            <h3 className="feature-title">Educational Content</h3>
            <p className="feature-description">
              Access comprehensive learning materials across multiple subjects. 
              Interactive lessons, detailed explanations, and structured content 
              to help you master any topic.
            </p>
            <div className="feature-highlights">
              <span className="highlight">Structured Lessons</span>
              <span className="highlight">Visual Learning</span>
              <span className="highlight">Progress Tracking</span>
            </div>
          </div>

          {/* AI Tutor */}
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3 className="feature-title">AI Tutor Chatbot</h3>
            <p className="feature-description">
              Get instant help from our intelligent AI tutor. Ask questions, 
              get explanations, and receive personalized guidance for any subject 
              or topic you're studying.
            </p>
            <div className="feature-highlights">
              <span className="highlight">24/7 Support</span>
              <span className="highlight">Smart Responses</span>
              <span className="highlight">Code Analysis</span>
            </div>
          </div>

          {/* Quiz System */}
          <div className="feature-card">
            <div className="feature-icon">❓</div>
            <h3 className="feature-title">Interactive Quizzes</h3>
            <p className="feature-description">
              Test your knowledge with our comprehensive quiz system. 
              Multiple choice questions, instant feedback, and detailed 
              explanations to reinforce your learning.
            </p>
            <div className="feature-highlights">
              <span className="highlight">Multiple Subjects</span>
              <span className="highlight">Instant Feedback</span>
              <span className="highlight">Performance Analytics</span>
            </div>
          </div>

          {/* Reports */}
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3 className="feature-title">Progress Reports</h3>
            <p className="feature-description">
              Track your learning progress with detailed reports and analytics. 
              Visual charts, performance metrics, and insights to help you 
              identify areas for improvement.
            </p>
            <div className="feature-highlights">
              <span className="highlight">Visual Analytics</span>
              <span className="highlight">Performance Tracking</span>
              <span className="highlight">PDF Reports</span>
            </div>
          </div>

          {/* Collaboration */}
          <div className="feature-card">
            <div className="feature-icon">👥</div>
            <h3 className="feature-title">Team Collaboration</h3>
            <p className="feature-description">
              Work together with classmates on group projects and assignments. 
              Real-time collaboration tools, shared workspaces, and team 
              communication features.
            </p>
            <div className="feature-highlights">
              <span className="highlight">Real-time Editing</span>
              <span className="highlight">Team Projects</span>
              <span className="highlight">Shared Workspaces</span>
            </div>
          </div>

          {/* Calendar */}
          <div className="feature-card">
            <div className="feature-icon">📅</div>
            <h3 className="feature-title">Smart Calendar</h3>
            <p className="feature-description">
              Organize your study schedule with our intelligent calendar. 
              Set reminders, track deadlines, and manage your academic 
              commitments efficiently.
            </p>
            <div className="feature-highlights">
              <span className="highlight">Event Management</span>
              <span className="highlight">Study Reminders</span>
              <span className="highlight">Deadline Tracking</span>
            </div>
          </div>

        </div>
      </div>

      {/* Getting Started Section */}
      <div className="getting-started-section">
        <h2 className="section-title">Ready to Start Learning?</h2>
        <div className="cta-buttons">
          <button className="cta-button primary">Explore Content</button>
          <button className="cta-button secondary">Take a Quiz</button>
          <button className="cta-button secondary">Chat with AI</button>
        </div>
      </div>
    </div>
  );
} 