import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, BarElement, ArcElement, PointElement, LineElement, Tooltip, Legend } from 'chart.js';
import { useState } from 'react';
Chart.register(CategoryScale, LinearScale, BarElement, ArcElement, PointElement, LineElement, Tooltip, Legend);

export default function Report() {
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Default/mock data
  const subjects = ['Data Structures', 'OS', 'DBMS', 'Networks', 'AI', 'ML'];
  const subjectScores = [88, 76, 92, 81, 67, 95];
  const topicCompletion = [12, 9, 14, 10, 7, 15];
  const totalTopics = [15, 12, 15, 12, 10, 15];
  const activityDates = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const activityCounts = [2, 4, 3, 5, 6, 2, 1];

  const generatePDF = async () => {
    setIsGeneratingPDF(true);
    setError('');
    setSuccess('');

    try {
      const studentName = localStorage.getItem('username') || 'Student';
      
      const response = await fetch('http://127.0.0.1:5000/api/generate-report-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          subjects,
          subjectScores,
          topicCompletion,
          totalTopics,
          activityDates,
          activityCounts,
          studentName
        })
      });

      const data = await response.json();

      if (data.success) {
        // Convert base64 to blob and download
        const pdfBlob = new Blob([Uint8Array.from(atob(data.pdf_data), c => c.charCodeAt(0))], {
          type: 'application/pdf'
        });
        
        const url = window.URL.createObjectURL(pdfBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = data.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        setSuccess('PDF report downloaded successfully!');
      } else {
        setError(data.error || 'Failed to generate PDF');
      }
    } catch (err) {
      console.error('Error generating PDF:', err);
      setError('Failed to generate PDF. Please try again.');
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 32 }}>
        <h2 style={{ textAlign: 'center', margin: 0 }}>📈 Super Duper Progress Report</h2>
        <button
          onClick={generatePDF}
          disabled={isGeneratingPDF}
          style={{
            background: isGeneratingPDF ? '#ccc' : 'linear-gradient(90deg, #007bff, #4a4e69)',
            color: 'white',
            border: 'none',
            borderRadius: 8,
            padding: '12px 24px',
            fontSize: 16,
            fontWeight: 600,
            cursor: isGeneratingPDF ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          {isGeneratingPDF ? '🔄 Generating...' : '📄 Download PDF'}
        </button>
      </div>

      {error && (
        <div style={{
          background: '#f8d7da',
          color: '#721c24',
          padding: '12px 16px',
          borderRadius: 8,
          marginBottom: 20,
          border: '1px solid #f5c6cb'
        }}>
          {error}
        </div>
      )}

      {success && (
        <div style={{
          background: '#d4edda',
          color: '#155724',
          padding: '12px 16px',
          borderRadius: 8,
          marginBottom: 20,
          border: '1px solid #c3e6cb'
        }}>
          {success}
        </div>
      )}
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