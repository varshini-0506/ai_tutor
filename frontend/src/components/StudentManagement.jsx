import React, { useState } from 'react';
import './StudentManagement.css';

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

  const openModal = (student) => {
    setSelectedStudent(student);
    document.body.classList.add('modal-open');
  };
  
  const closeModal = () => {
    setSelectedStudent(null);
    document.body.classList.remove('modal-open');
  };

  return (
    <div className="student-management">
      <h2>Student List</h2>
      <div className="student-table-container">
        <table className="student-table">
          <thead>
            <tr>
              <th></th>
              <th>Name</th>
              <th>Email</th>
              <th>Class</th>
              <th>Progress</th>
              <th>Last Login</th>
            </tr>
          </thead>
          <tbody>
            {students.map(student => (
              <tr key={student.id} onClick={() => openModal(student)}>
                <td><span className="student-avatar-sm">{getInitials(student.name)}</span></td>
                <td>{student.name}</td>
                <td>{student.email}</td>
                <td>{student.class}</td>
                <td>{student.progress}</td>
                <td>{student.lastLogin}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal for student details */}
      {selectedStudent && (
        <div className="student-modal-overlay" onClick={closeModal}>
          <div className="student-modal-content" onClick={e => e.stopPropagation()}>
            <div className="student-modal-header">
              <h3>Student Details</h3>
              <button onClick={closeModal} className="student-close-button">&times;</button>
            </div>
            <div className="student-modal-body">
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