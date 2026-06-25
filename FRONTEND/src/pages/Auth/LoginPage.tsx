import React from 'react';
import LoginForm from '../../components/Auth/LoginForm';
import styles from '../../components/Auth/auth.module.css';

export const LoginPage: React.FC = () => {
  return (
    <div className={styles.authContainer}>
      <div className={styles.leftPanel}>
        <div className={styles.floatingOrbs}>
          <div className={styles.orb1} />
          <div className={styles.orb2} />
        </div>
        <div style={{ position: 'relative', zIndex: 10 }}>
          <h1 className={styles.heroTitle}>GradSphere</h1>
          <p className={styles.heroDesc}>
            Your comprehensive university student assistance platform. Manage welfare schemes,
            prepare for interviews, apply for internships, and store your academic records in DigiLocker.
          </p>
        </div>
      </div>
      <div className={styles.rightPanel}>
        <LoginForm />
      </div>
    </div>
  );
};

export default LoginPage;
