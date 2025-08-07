import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { 
  Chart, 
  ArcElement, 
  Tooltip, 
  Legend, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  PointElement, 
  LineElement 
} from 'chart.js';
import { useAuth } from './AuthContext.jsx';
import './Report.css';

// Register all necessary Chart.js components
Chart.register(
  ArcElement, 
  Tooltip, 
  Legend, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  PointElement, 
  LineElement
);

// Main Report Component
export default function Report() {
  const { user } = useAuth();
  const isTeacher = user?.role === 'teacher';
  
  return (
    <div className="reports-container printable-report">
      {isTeacher ? <TeacherDashboard /> : <StudentDashboard />}
    </div>
  );
}

// Student Dashboard Component
function StudentDashboard() {
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const subjectMasteryData = {
    labels: ['Data Structures', 'Operating Systems', 'Database Management Systems', 'Computer Networks', 'Computer Organization & Architecture', 'Software Engineering'],
    datasets: [{
      label: 'Mastery',
      data: [88, 75, 92, 80, 85, 78],
      backgroundColor: ['#a6cee3', '#b2df8a', '#fdbf6f', '#cab2d6', '#fb9a99', '#99d8c9'],
      borderRadius: 6,
    }],
  };

  const topicCompletionData = {
    labels: ['Data Structures', 'Operating Systems', 'Database Management Systems', 'Computer Networks', 'Computer Organization & Architecture', 'Software Engineering'],
    datasets: [{
      data: [18, 15, 22, 15, 12, 16],
      backgroundColor: ['#a6cee3', '#b2df8a', '#fdbf6f', '#cab2d6', '#fb9a99', '#99d8c9'],
      borderColor: '#fff',
      borderWidth: 3,
    }],
  };
  
  const weeklyActivityData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
      label: 'Activities',
      data: [3, 5, 4, 6, 7, 2, 4],
      fill: true,
      backgroundColor: 'rgba(30, 64, 175, 0.1)',
      borderColor: '#1e40af',
      tension: 0.4,
    }],
  };

  const barOptions = {
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true, max: 100 } },
  };

  const doughnutOptions = {
    maintainAspectRatio: false,
    cutout: '70%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: { boxWidth: 12, padding: 20 },
      },
    },
  };
  
  const lineOptions = {
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true, max: 10 } },
  };

  const generatePDF = async () => {
    setIsGeneratingPDF(true);
    setError('');
    setSuccess('');

    try {
      const studentName = localStorage.getItem('username') || 'Student';
      const sanitizedStudentName = studentName.replace(/[^a-zA-Z0-9\s]/g, '').trim() || 'Student';
      
      const requestData = {
        student_name: sanitizedStudentName
      };
      
      console.log('Sending data to backend:', requestData);
      
      let jsonString;
      try {
        jsonString = JSON.stringify(requestData);
        console.log('JSON string being sent:', jsonString);
      } catch (jsonError) {
        console.error('JSON stringify error:', jsonError);
        setError('Failed to prepare data for PDF generation. Please try again.');
        setIsGeneratingPDF(false);
        return;
      }
      
      const response = await fetch('https://ai-tutor-backend-m4rr.onrender.com/api/generate-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonString
      });

      const data = await response.json();

      if (data.success) {
        // Download the PDF file
        const response2 = await fetch(`https://ai-tutor-backend-m4rr.onrender.com/api/download-report/${data.report_id}`);
        const pdfBlob = await response2.blob();
        
        const url = window.URL.createObjectURL(pdfBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = data.filename || `report_${sanitizedStudentName}.pdf`;
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
    <>
      <div className="reports-header no-print">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>Your Progress Dashboard</h2>
          <button
            onClick={generatePDF}
            disabled={isGeneratingPDF}
            className="download-pdf-btn"
          >
            {isGeneratingPDF ? '🔄 Generating...' : '📄 Download PDF'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      {success && (
        <div className="success-banner">
          {success}
        </div>
      )}

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Subject Mastery</h3>
          <Bar data={subjectMasteryData} options={barOptions} />
        </div>
        <div className="dashboard-card">
          <h3>Topic Completion</h3>
          <Doughnut data={topicCompletionData} options={doughnutOptions} />
        </div>
      </div>
      
      <div className="dashboard-card activity-chart">
        <h3>Weekly Learning Activity</h3>
        <Line data={weeklyActivityData} options={lineOptions} />
      </div>

      <style>{`
        @media print {
          body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
          .reports-container { padding: 0 !important; }
          .no-print, .navbar { display: none !important; }
          .dashboard-card { box-shadow: none !important; border: 1px solid #e2e8f0; }
        }
      `}</style>
    </>
  );
}

// Teacher Dashboard Component
function TeacherDashboard() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [selectedReport, setSelectedReport] = useState(null);
  const [remarkText, setRemarkText] = useState('');
  const [showRemarkModal, setShowRemarkModal] = useState(false);

  // Clear message after 5 seconds
  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => {
        setMessage('');
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  const fetchReports = async () => {
    try {
      const token = sessionStorage.getItem('token');
      const response = await axios.get(
        'https://ai-tutor-backend-m4rr.onrender.com/api/reports',
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setReports(response.data);
    } catch (error) {
      setMessage(
        `❌ Error loading reports: ${
          error.response?.data?.error || error.message
        }`
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const viewReportInModal = async (report) => {
    try {
      const token = sessionStorage.getItem('token');
      const response = await axios.get(
        `https://ai-tutor-backend-m4rr.onrender.com/api/view-report/${report.id}`,
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob',
        }
      );
      const file = new Blob([response.data], { type: 'application/pdf' });
      const fileURL = URL.createObjectURL(file);
      window.open(fileURL, '_blank');
    } catch (error) {
      setMessage(`❌ Error viewing report: ${error.response?.data?.error || 'Could not load PDF'}`);
    }
  };

  const downloadReport = async (reportId) => {
    try {
              const response = await axios.get(`https://ai-tutor-backend-m4rr.onrender.com/api/download-report/${reportId}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${reportId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setMessage(`❌ Download error: ${error.response?.data?.error || error.message}`);
    }
  };

  const deleteReport = async (reportId) => {
    if (!window.confirm('Are you sure you want to delete this report?')) return;
    try {
      const token = sessionStorage.getItem('token');
              await axios.delete(`https://ai-tutor-backend-m4rr.onrender.com/api/reports/${reportId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setReports(reports.filter(r => r.id !== reportId));
      setMessage('✅ Report deleted successfully');
    } catch (error) {
      setMessage(`❌ Delete error: ${error.response?.data?.error || error.message}`);
    }
  };

  const openRemarkModal = (report) => {
    setSelectedReport(report);
    setRemarkText(report.remarks || '');
    setShowRemarkModal(true);
  };

  const closeRemarkModal = () => {
    setShowRemarkModal(false);
    setSelectedReport(null);
    setRemarkText('');
  };

  const addRemark = async () => {
    if (!remarkText.trim()) {
      setMessage('❌ Please enter a remark');
      return;
    }

    try {
      const token = sessionStorage.getItem('token');
      const response = await axios.post(
        `https://ai-tutor-backend-m4rr.onrender.com/api/reports/${selectedReport.id}/remark`,
        { remark: remarkText },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Update the report in the local state immediately
      setReports(prevReports => 
        prevReports.map(r => 
          r.id === selectedReport.id 
            ? { ...r, remarks: remarkText }
            : r
        )
      );

      setMessage('✅ Remark added successfully');
      setShowRemarkModal(false);
      setRemarkText('');
      setSelectedReport(null);

      // Refresh the reports list to ensure everything is in sync
      setTimeout(() => {
        fetchReports();
      }, 100);
    } catch (error) {
      setMessage(`❌ Error adding remark: ${error.response?.data?.error || error.message}`);
    }
  };

  if (loading) return <div>Loading reports...</div>;

  return (
    <>
      <div className="reports-header">
        <h2>📊 Student Reports Dashboard</h2>
      </div>
      
      {message && (
        <div className="message-banner" style={{ 
          color: message.includes('❌') ? 'red' : 'green', 
          backgroundColor: message.includes('❌') ? '#fee' : '#efe'
        }}>
          {message}
        </div>
      )}

      <div className="report-grid">
        {reports.length > 0 ? reports.map((report) => (
          <div key={report.id} className="report-card">
            <div className="report-card-header">
              <h4>📊 {report.student_name}</h4>
              <span>{new Date(report.created_at).toLocaleDateString()}</span>
            </div>
            <p className="report-card-summary">
              {report.remarks ? `Remark: "${report.remarks}"` : "No remarks added yet."}
            </p>
            <div className="report-card-actions">
              <button onClick={() => viewReportInModal(report)} className="btn-view">👁️ View</button>
              <button onClick={() => openRemarkModal(report)} className="btn-remark">✏️ Remarks</button>
              <button onClick={() => downloadReport(report.id)} className="btn-download">📥 Download</button>
              <button onClick={() => deleteReport(report.id)} className="btn-delete">🗑️ Delete</button>
            </div>
          </div>
        )) : (
          <div className="no-reports-message">
            <p>No reports found. Reports will appear here once students complete their assessments.</p>
          </div>
        )}
      </div>

      {/* Remark Modal */}
      {showRemarkModal && (
        <div className="remark-modal-overlay">
          <div className="remark-modal">
            <h3>Add Remark for {selectedReport?.student_name}</h3>
            <textarea
              value={remarkText}
              onChange={(e) => setRemarkText(e.target.value)}
              placeholder="Enter your remark here..."
              className="remark-textarea"
            />
            <div className="modal-actions">
              <button
                onClick={() => {
                  setShowRemarkModal(false);
                  setRemarkText('');
                  setSelectedReport(null);
                }}
                className="modal-cancel-btn"
              >
                Cancel
              </button>
              <button
                onClick={addRemark}
                className="modal-save-btn"
              >
                Save Remark
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}