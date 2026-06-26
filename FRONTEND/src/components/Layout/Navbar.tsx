import React, { useState } from 'react';
import styles from './navbar.module.css';
import { Search, Bell, Menu, X, User } from 'lucide-react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import { logout } from '../../redux/slices/authSlice';
import { useNavigate, Link } from 'react-router-dom';

export const Navbar: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, isLoggedIn } = useSelector((state: RootState) => state.auth);

  const toggleMenu = () => setMobileOpen(!mobileOpen);
  
  const handleLogout = () => {
    dispatch(logout());
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <nav className={styles.navbar}>
      <div className={styles.container}>
        <div className={styles.brandSection}>
          <button className={styles.menuButton} onClick={toggleMenu} aria-label="Toggle menu">
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
          <Link to="/" className={styles.brand}>
            <img src="/logo.svg" alt="GRADSphere Logo" className={styles.logoImage} />
          </Link>
        </div>

        <div className={styles.searchBar}>
          <Search size={18} className={styles.searchIcon} />
          <input type="text" placeholder="Search schemes, jobs, files..." className={styles.searchInput} />
        </div>

        <div className={styles.actions}>
          <button className={styles.iconButton} aria-label="Search" style={{ display: 'none' }}>
            <Search size={20} />
          </button>
          <button className={styles.iconButton} aria-label="Notifications">
            <Bell size={20} />
            <span className={styles.badge}></span>
          </button>

          {isLoggedIn ? (
            <div className={styles.profileContainer}>
              <button 
                className={styles.avatarButton} 
                onClick={() => setShowProfileMenu(!showProfileMenu)}
                aria-label="Profile menu"
              >
                {user?.name ? (
                  <div className={styles.avatarText}>{user.name[0].toUpperCase()}</div>
                ) : (
                  <User size={20} />
                )}
              </button>

              {showProfileMenu && (
                <div className={styles.profileDropdown}>
                  <div className={styles.profileHeader}>
                    <p className={styles.profileName}>{user?.name || 'Student'}</p>
                    <p className={styles.profileEmail}>{user?.email}</p>
                  </div>
                  <button onClick={handleLogout} className={styles.dropdownItem}>
                    Logout
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link to="/login" className={styles.loginBtn}>Sign In</Link>
          )}
        </div>
      </div>

      {mobileOpen && (
        <div className={styles.mobileMenu}>
          <div className={styles.mobileSearch}>
            <Search size={18} className={styles.searchIcon} />
            <input type="text" placeholder="Search..." className={styles.searchInput} />
          </div>
          <Link to="/" className={styles.mobileLink} onClick={() => setMobileOpen(false)}>Dashboard</Link>
          <Link to="/welfare" className={styles.mobileLink} onClick={() => setMobileOpen(false)}>Welfare Schemes</Link>
          <Link to="/welfare/chat" className={styles.mobileLink} onClick={() => setMobileOpen(false)}>Welfare Chat</Link>
          <Link to="/internships" className={styles.mobileLink} onClick={() => setMobileOpen(false)}>Internships</Link>
          <Link to="/internships/chat" className={styles.mobileLink} onClick={() => setMobileOpen(false)}>Internships Chat</Link>
          <Link to="/interview" className={styles.mobileLink} onClick={() => setMobileOpen(false)}>Interview Prep</Link>
          <Link to="/digilocker" className={styles.mobileLink} onClick={() => setMobileOpen(false)}>DigiLocker</Link>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
