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
      <h1>Welcome to AI Tutor</h1>
      <p>Your personal learning assistant with quizzes, reports, and collaboration!</p>
    </div>
  );
} 