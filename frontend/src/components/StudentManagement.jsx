import React, { useState } from 'react';

// Mock student data
const mockStudents = [
  { id: 1, name: 'Alice Johnson', email: 'alice@example.com', class: 'Math 101', progress: '85%', lastLogin: '2024-01-15' },
  { id: 2, name: 'Bob Smith', email: 'bob@example.com', class: 'Math 101', progress: '72%', lastLogin: '2024-01-14' },
  { id: 3, name: 'Charlie Brown', email: 'charlie@example.com', class: 'Math 101', progress: '91%', lastLogin: '2024-01-15' },
  { id: 4, name: 'Diana Prince', email: 'diana@example.com', class: 'Math 101', progress: '68%', lastLogin: '2024-01-13' },
];

function getInitials(name) {
  return name.split(' ').map(n => n[0]).join('').toUpperCase();
}

export default function StudentManagement() {
  const [students] = useState(mockStudents);
  const [selectedStudent, setSelectedStudent] = useState(null);

  const openModal = (student) => setSelectedStudent(student);
  const closeModal = () => setSelectedStudent(null);

  return (
    <div className="student-management">
      <h2>Student List</h2>
      <div style={{ overflowX: 'auto', marginTop: 24 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.07)' }}>
          <thead style={{ background: '#f4f6fa' }}>
            <tr>
              <th style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}></th>
              <th style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>Name</th>
              <th style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>Email</th>
              <th style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>Class</th>
              <th style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>Progress</th>
              <th style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>Last Login</th>
            </tr>
          </thead>
          <tbody>
            {students.map(student => (
              <tr key={student.id} style={{ cursor: 'pointer' }} onClick={() => openModal(student)}>
                <td style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}><span className="student-avatar-sm">{getInitials(student.name)}</span></td>
                <td style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>{student.name}</td>
                <td style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>{student.email}</td>
                <td style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>{student.class}</td>
                <td style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>{student.progress}</td>
                <td style={{ padding: '12px', borderBottom: '1px solid #e9ecef' }}>{student.lastLogin}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal for student details */}
      {selectedStudent && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: 400 }}>
            <div className="modal-header">
              <h3>Student Details</h3>
              <button onClick={closeModal} className="close-button">&times;</button>
            </div>
            <div className="modal-body" style={{ display: 'block' }}>
              <div className="student-avatar">{getInitials(selectedStudent.name)}</div>
              <p><strong>Name:</strong> {selectedStudent.name}</p>
              <p><strong>Email:</strong> {selectedStudent.email}</p>
              <p><strong>Class:</strong> {selectedStudent.class}</p>
              <p><strong>Progress:</strong> {selectedStudent.progress}</p>
              <p><strong>Last Login:</strong> {selectedStudent.lastLogin}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 