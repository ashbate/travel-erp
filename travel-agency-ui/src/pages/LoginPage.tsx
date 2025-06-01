import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser } from '../services/apiService';
import { useAuthStore } from '../store/authStore';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { setToken, setUser } = useAuthStore();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      const response = await loginUser({ username, password });
      setToken(response.access_token);
      // Fetch user details after login or decode token if it contains user info
      // For now, we'll assume token is the primary auth proof.
      // setUser({ username }); // Or fetch from a /users/me endpoint
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
      console.error('Login error:', err);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <form onSubmit={handleSubmit} style={{ padding: '2rem', boxShadow: '0 0 10px rgba(0,0,0,0.1)', borderRadius: '8px', background: 'white', width: '300px' }}>
        <h2>Login</h2>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="username">Username:</label><br />
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={{ width: '100%', padding: '0.5rem', boxSizing: 'border-box' }}
          />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="password">Password:</label><br />
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '0.5rem', boxSizing: 'border-box' }}
          />
        </div>
        <button type="submit" style={{ width: '100%', padding: '0.75rem', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Login
        </button>
      </form>
    </div>
  );
};

export default LoginPage;
