import React from 'react';
import { useAuthStore } from '../store/authStore';
import { useNavigate, Link } from 'react-router-dom'; // Import Link

const HomePage: React.FC = () => {
  const { token, clearAuth } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  return (
    <div style={{padding: '2rem'}}>
      <h1>Welcome to the Travel Agency App!</h1>
      <p>You are logged in.</p>
      <p>Your token (first 20 chars): {token?.substring(0, 20)}...</p>
      <nav>
        <ul>
          <li><Link to="/ai-tour-creation">Create Tour with AI</Link></li>
          {/* Add links to other features later */}
        </ul>
      </nav>
      <button onClick={handleLogout} style={{marginTop: '1rem'}}>Logout</button>
    </div>
  );
};

export default HomePage;
