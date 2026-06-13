import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, History, LogOut, Cpu, BookOpen, GraduationCap, Users } from 'lucide-react';

const DashboardLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navLinkStyle = ({isActive}) => ({
    display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem 1rem', 
    borderRadius: '8px', textDecoration: 'none', color: isActive ? 'white' : 'var(--text-muted)',
    backgroundColor: isActive ? 'var(--primary-color)' : 'transparent',
    transition: 'all 0.2s'
  });

  return (
    <div className="app-container">
      <aside className="sidebar glass-panel" style={{ borderRadius: 0, borderTop: 'none', borderBottom: 'none', borderLeft: 'none' }}>
        <div style={{ padding: '2rem', display: 'flex', alignItems: 'center', gap: '0.75rem', borderBottom: '1px solid var(--border-color)' }}>
          <Cpu color="var(--primary-color)" size={28} />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', margin: 0 }}>AdaptIQ</h2>
        </div>
        
        <nav style={{ padding: '1.5rem 1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
          
          {user?.role === 'MANAGER' ? (
            <>
              <NavLink to="/manager" style={navLinkStyle}>
                <Users size={20} />
                Team Insights
              </NavLink>
            </>
          ) : (
            <>
              <NavLink to="/" end style={navLinkStyle}>
                <LayoutDashboard size={20} />
                Learning Hub
              </NavLink>
              
              <NavLink to="/plan" style={navLinkStyle}>
                <BookOpen size={20} />
                Generate Plan
              </NavLink>
              
              <NavLink to="/assess" style={navLinkStyle}>
                <GraduationCap size={20} />
                Assessment
              </NavLink>
              
              <NavLink to="/history" style={navLinkStyle}>
                <History size={20} />
                Job History
              </NavLink>
            </>
          )}

        </nav>

        <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border-color)' }}>
          <div style={{ marginBottom: '1rem' }}>
            <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--text-main)' }}>{user?.email}</p>
          </div>
          <button 
            onClick={handleLogout}
            className="btn-secondary" 
            style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default DashboardLayout;
