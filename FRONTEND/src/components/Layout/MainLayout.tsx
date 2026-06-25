import React from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import Footer from './Footer';
import { Outlet } from 'react-router-dom';
import styles from '../../styles/layout.module.css';

export interface MainLayoutProps {
  children?: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className={styles.layout}>
      <Navbar />
      <div style={{ display: 'flex', flexGrow: 1 }}>
        <Sidebar />
        <main className={styles.mainContent}>
          {children || <Outlet />}
          <Footer />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
