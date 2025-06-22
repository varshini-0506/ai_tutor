import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Chart, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, LineElement, PointElement } from 'chart.js';
import { useAuth } from './AuthContext.jsx';
import { Pie, Bar, Doughnut, Line } from 'react-chartjs-2';

Chart.register(CategoryScale, LinearScale, BarElement, ArcElement, PointElement, LineElement, Tooltip, Legend);

export default function Report() {
  const { user } = useAuth();
  const role = user ? user.role : null;
  console.log(`Report component is rendering for role: "${role}"`);

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '2rem' }}>
      {role !== 'teacher' &&
        <h2 style={{ textAlign: 'center', marginBottom: 32 }}>
          📊 Your Learning Progress Report
        </h2>
      }
      
      {role === 'teacher' && (
        <div>
          <h2 style={{ textAlign: 'center', marginBottom: 32 }}>
            📊 Student Reports Dashboard
          </h2>
          
          {/* Teacher-specific report list */}
          <TeacherReportList />
        </div>
      )}
      
      {role !== 'teacher' && (
        <div>
          {/* Student-specific report view */}
          <StudentReportView />
        </div>
      )}
    </div>
  );
}

function TeacherReportList() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const token = sessionStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/reports', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setReports(response.data);
    } catch (error) {
      setMessage(`❌ Error loading reports: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const viewReportInModal = (report) => {
    window.open(`http://localhost:5000/api/view-report/${report.id}`, '_blank');
  };

  const downloadReport = async (reportId) => {
    try {
      const response = await axios.get(`http://localhost:5000/api/download-report/${reportId}`, {
        responseType: 'blob'
      });

      // Create download link
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
      await axios.delete(`http://localhost:5000/api/reports/${reportId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setReports(reports.filter(r => r.id !== reportId));
      setMessage('✅ Report deleted successfully');
    } catch (error) {
      setMessage(`❌ Delete error: ${error.response?.data?.error || error.message}`);
    }
  };

  if (loading) return <div>Loading reports...</div>;
  if (message) return <div style={{ color: message.includes('❌') ? 'red' : 'green', marginBottom: 16 }}>{message}</div>;

  return (
    <div>
      {reports.length === 0 ? (
        <div className="no-reports-message">
          <p>No reports found. Reports will appear here once students complete their assessments.</p>
        </div>
      ) : (
        <div className="report-grid">
          {reports.map((report) => (
            <div key={report.id} className="report-card">
              <div className="report-card-header">
                <h4>📊 {report.student_name}</h4>
                <span>{new Date(report.created_at).toLocaleDateString()}</span>
              </div>
              <p className="report-card-summary">
                {report.remarks ? `Remark: "${report.remarks}"` : "No remarks added yet."}
              </p>
              <div className="report-card-actions">
                <button onClick={() => viewReportInModal(report)} className="btn-view">
                  👁️ View
                </button>
                <button onClick={() => downloadReport(report.id)} className="btn-download">
                  📥 Download
                </button>
                <button onClick={() => deleteReport(report.id)} className="btn-delete">
                  🗑️ Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StudentReportView() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchStudentReports();
  }, []);

  const fetchStudentReports = async () => {
    try {
      const token = sessionStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/student-reports', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setReports(response.data);
    } catch (error) {
      setMessage(`❌ Error loading reports: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async (reportId) => {
    try {
      const response = await axios.get(`http://localhost:5000/api/download-report/${reportId}`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `my_report_${reportId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setMessage(`❌ Download error: ${error.response?.data?.error || error.message}`);
    }
  };

  if (loading) return <div>Loading your reports...</div>;
  if (message) return <div style={{ color: message.includes('❌') ? 'red' : 'green', marginBottom: 16 }}>{message}</div>;

  return (
    <div>
      {reports.length === 0 ? (
        <div className="no-reports-message">
          <p>No reports available yet. Complete some quizzes to generate your first report!</p>
        </div>
      ) : (
        <div>
          {reports.map((report) => (
            <div key={report.id} className="student-report-item">
              <div className="report-info">
                <h4>📊 Progress Report - {new Date(report.created_at).toLocaleDateString()}</h4>
                <span className="report-date">Generated on {new Date(report.created_at).toLocaleString()}</span>
              </div>
              
              {report.remarks && (
                <div className="teacher-remark">
                  <h5>💬 Teacher's Remark:</h5>
                  <div className="remark-bubble">
                    <p>{report.remarks}</p>
                  </div>
                </div>
              )}
              
              <div className="report-actions">
                <button onClick={() => downloadReport(report.id)} className="btn-download">
                  📥 Download Report
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 