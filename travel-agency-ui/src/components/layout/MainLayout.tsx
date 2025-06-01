import React, { ReactNode } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';

interface MainLayoutProps {
  children: ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <div style={{ display: 'flex', flexGrow: 1 }}>
        <Sidebar />
        <main style={{ flexGrow: 1, padding: '2rem', background: '#fff' }}>
          {children}
        </main>
      </div>
      {/* Optional Footer could go here */}
    </div>
  );
};

export default MainLayout;
