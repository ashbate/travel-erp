import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const Header: React.FC = () => {
  const { user, token, clearAuth } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  return (
    <header style={{
      background: '#333',
      color: 'white',
      padding: '1rem 2rem',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
    }}>
      <Link to="/" style={{ color: 'white', textDecoration: 'none', fontSize: '1.5rem' }}>
        Travel Agency App
      </Link>
      <nav>
        {token ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {user && <span>Hello, {user.username || 'User'}</span>} {/* Assuming user object has username */}
            <button onClick={handleLogout} style={{ background: '#555', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '4px', cursor: 'pointer' }}>
              Logout
            </button>
          </div>
        ) : (
          <Link to="/login" style={{ color: 'white', textDecoration: 'none' }}>Login</Link>
        )}
      </nav>
    </header>
  );
};

export default Header;
