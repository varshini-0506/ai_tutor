import React, { useState } from 'react';
import axios from 'axios';

function Signup() {
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    role: ''
  });

  const [message, setMessage] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Simple validation
    if (!form.name || !form.email || !form.password || !form.role) {
      setMessage('Please fill in all fields.');
      return;
    }

    try {
      const res = await axios.post('http://localhost:5000/api/auth/signup', form);
      setMessage(res.data.msg);
      setForm({ name: '', email: '', password: '', role: '' }); // Clear form
    } catch (err) {
      setMessage(err.response?.data?.msg || 'Signup failed');
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '400px', margin: 'auto' }}>
      <h2>Signup</h2>
      {message && <p>{message}</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="name"
          placeholder="Name"
          value={form.name}
          onChange={handleChange}
          required
        /><br /><br />

        <input
          type="email"
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          required
        /><br /><br />

        <input
          type="password"
          name="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
          required
        /><br /><br />

        <select name="role" value={form.role} onChange={handleChange} required>
          <option value="">Select Role</option>
          <option value="student">Student</option>
          <option value="teacher">Teacher</option>
        </select><br /><br />

        <button type="submit">Signup</button>
      </form>
    </div>
  );
}

export default Signup;
