import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, BarElement, ArcElement, PointElement, LineElement, Tooltip, Legend } from 'chart.js';
Chart.register(CategoryScale, LinearScale, BarElement, ArcElement, PointElement, LineElement, Tooltip, Legend);

export default function Report() {
  // Default/mock data
  const subjects = ['Data Structures', 'OS', 'DBMS', 'Networks', 'AI', 'ML'];
  const subjectScores = [88, 76, 92, 81, 67, 95];
  const topicCompletion = [12, 9, 14, 10, 7, 15];
  const totalTopics = [15, 12, 15, 12, 10, 15];
  const activityDates = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const activityCounts = [2, 4, 3, 5, 6, 2, 1];

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '2rem' }}>
      <h2 style={{ textAlign: 'center', marginBottom: 32 }}>📈 Super Duper Progress Report</h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32, marginBottom: 40 }}>
        {/* Bar Chart: Subject Scores */}
        <div style={{ background: '#fff', borderRadius: 16, boxShadow: '0 2px 12px rgba(0,0,0,0.07)', padding: 24 }}>
          <h3 style={{ textAlign: 'center', marginBottom: 16 }}>Subject Mastery</h3>
          <Bar
            data={{
              labels: subjects,
              datasets: [{
                label: 'Score (%)',
                data: subjectScores,
                backgroundColor: [
                  '#a5d8ff', '#b2f2bb', '#ffd6a5', '#d0bfff', '#ffb5e8', '#b5ead7'
                ],
                borderRadius: 8,
              }],
            }}
            options={{
              responsive: true,
              plugins: { legend: { display: false } },
              scales: { y: { min: 0, max: 100, ticks: { stepSize: 20 } } },
            }}
            height={220}
          />
        </div>
        {/* Doughnut Chart: Topic Completion */}
        <div style={{ background: '#fff', borderRadius: 16, boxShadow: '0 2px 12px rgba(0,0,0,0.07)', padding: 24 }}>
          <h3 style={{ textAlign: 'center', marginBottom: 16 }}>Topic Completion</h3>
          <Doughnut
            data={{
              labels: subjects,
              datasets: [{
                label: 'Topics Completed',
                data: topicCompletion,
                backgroundColor: [
                  '#a5d8ff', '#b2f2bb', '#ffd6a5', '#d0bfff', '#ffb5e8', '#b5ead7'
                ],
                borderWidth: 2,
              }],
            }}
            options={{
              cutout: '70%',
              plugins: {
                legend: { position: 'bottom' },
              },
            }}
            height={220}
          />
          <div style={{ textAlign: 'center', marginTop: 12, fontWeight: 500, color: '#222' }}>
            {subjects.map((s, i) => (
              <div key={s} style={{ fontSize: 14 }}>
                {s}: {topicCompletion[i]} / {totalTopics[i]} topics
              </div>
            ))}
          </div>
        </div>
      </div>
      {/* Line Chart: Activity Over Time */}
      <div style={{ background: '#fff', borderRadius: 16, boxShadow: '0 2px 12px rgba(0,0,0,0.07)', padding: 24, marginBottom: 32 }}>
        <h3 style={{ textAlign: 'center', marginBottom: 16 }}>Weekly Activity</h3>
        <Line
          data={{
            labels: activityDates,
            datasets: [{
              label: 'Lessons/Quizzes Completed',
              data: activityCounts,
              fill: true,
              borderColor: '#4f8cff',
              backgroundColor: 'rgba(79,140,255,0.12)',
              tension: 0.4,
              pointRadius: 5,
              pointBackgroundColor: '#4f8cff',
            }],
          }}
          options={{
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { min: 0, max: 8, ticks: { stepSize: 2 } } },
          }}
          height={180}
        />
      </div>
      <div style={{ textAlign: 'center', color: '#4a4e69', fontWeight: 600, fontSize: 18 }}>
        🚀 Keep up the great work! Your learning journey is on fire!
      </div>
    </div>
  );
} 