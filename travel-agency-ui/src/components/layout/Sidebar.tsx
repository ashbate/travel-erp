import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const linkStyle = {
    display: 'block',
    padding: '0.75rem 1.5rem',
    color: '#333',
    textDecoration: 'none',
    borderBottom: '1px solid #eee',
  };

  const activeLinkStyle = {
    fontWeight: 'bold',
    backgroundColor: '#e9ecef',
  };

  return (
    <aside style={{
      width: '220px',
      background: '#f8f9fa',
      borderRight: '1px solid #dee2e6',
      height: 'calc(100vh - 60px)', // Assuming header height is approx 60px
      paddingTop: '1rem',
    }}>
      <nav>
        <NavLink
          to="/"
          style={({ isActive }) => isActive ? {...linkStyle, ...activeLinkStyle} : linkStyle}
        >
          Home (Dashboard)
        </NavLink>
        <NavLink
          to="/ai-tour-creation"
          style={({ isActive }) => isActive ? {...linkStyle, ...activeLinkStyle} : linkStyle}
        >
          AI Tour Creation
        </NavLink>
        <NavLink
          to="/tours"
          style={({ isActive }) => isActive ? {...linkStyle, ...activeLinkStyle} : linkStyle}
        >
          Manage Tours
        </NavLink>
        {/* Add more links as pages are created */}
        {/* Example: <NavLink to="/bookings" style={linkStyle}>Manage Bookings</NavLink> */}
      </nav>
    </aside>
  );
};

export default Sidebar;
