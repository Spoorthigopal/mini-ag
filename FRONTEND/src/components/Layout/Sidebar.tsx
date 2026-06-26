import React, { useState, useEffect } from 'react';
import styles from './sidebar.module.css';
import { LogOut, Home, Gift, Briefcase, FileText, Shield, Sparkles, Menu } from 'lucide-react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { logout } from '../../redux/slices/authSlice';

export const Sidebar: React.FC = () => {
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [open, setOpen] = useState(!isMobile);
  
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleResize = () => {
    const mobile = window.innerWidth <= 768;
    setIsMobile(mobile);
    if (!mobile) {
      setOpen(true);
    } else {
      setOpen(false);
    }
  };

  useEffect(() => {
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggle = () => setOpen(!open);

  const handleLogout = () => {
    dispatch(logout());
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <>
      {isMobile && (
        <button className={styles.toggleButton} onClick={toggle} aria-label="Toggle Sidebar">
          <Menu size={24} />
        </button>
      )}
      <aside className={`${styles.sidebar} ${open ? styles.sidebarOpen : ''}`}>
        <div>
          <div className={styles.title}>Modules</div>
          <nav className={styles.section}>
            <NavLink 
              to="/" 
              className={({ isActive }) => `${styles.link} ${isActive ? styles.activeLink : ''}`}
            >
              <Home size={18} /> Dashboard
            </NavLink>
            <NavLink 
              to="/welfare" 
              className={({ isActive }) => `${styles.link} ${isActive ? styles.activeLink : ''}`}
            >
              <Gift size={18} /> Welfare Schemes
            </NavLink>
            <NavLink 
              to="/internships" 
              className={({ isActive }) => `${styles.link} ${isActive ? styles.activeLink : ''}`}
            >
              <Briefcase size={18} /> Internships
            </NavLink>
            <NavLink 
              to="/interview" 
              className={({ isActive }) => `${styles.link} ${isActive ? styles.activeLink : ''}`}
            >
              <Sparkles size={18} /> Interview Prep
            </NavLink>
            <NavLink 
              to="/digilocker" 
              className={({ isActive }) => `${styles.link} ${isActive ? styles.activeLink : ''}`}
            >
              <Shield size={18} /> DigiLocker
            </NavLink>
          </nav>

          <div className={styles.title}>Quick Actions</div>
          <nav className={styles.section}>
            <NavLink 
              to="/welfare/chat" 
              className={({ isActive }) => `${styles.link} ${isActive ? styles.activeLink : ''}`}
            >
              <Sparkles size={18} /> Scheme Assistant
            </NavLink>
            <NavLink 
              to="/internships/chat" 
              className={({ isActive }) => `${styles.link} ${isActive ? styles.activeLink : ''}`}
            >
              <FileText size={18} /> Resume Helper
            </NavLink>
          </nav>
        </div>

        <button className={styles.logout} onClick={handleLogout}>
          <LogOut size={18} /> Logout
        </button>
      </aside>
    </>
  );
};

export default Sidebar;
