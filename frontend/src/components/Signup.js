import React, { useState } from 'react';
import axios from 'axios';

function Signup() {
  const [form, setForm] = useState({ name: '', email: '', password: '' });

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      const res = await axios.post('http://localhost:5000/api/auth/signup', form);
      alert(res.data.msg);
    } catch (err) {
      alert(err.response?.data?.msg || "Signup error");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Signup</h3>
      <input name="name" placeholder="Name" onChange={handleChange} required /><br />
      <input name="email" placeholder="Email" onChange={handleChange} required /><br />
      <input type="password" name="password" placeholder="Password" onChange={handleChange} required /><br />
      <button type="submit">Signup</button>
    </form>
  );
}

export default Signup;
