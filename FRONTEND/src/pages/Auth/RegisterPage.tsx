import React from 'react';
import RegisterForm from '../../components/Auth/RegisterForm';
import styles from '../../components/Auth/auth.module.css';

export const RegisterPage: React.FC = () => {
  return (
    <div className={styles.authContainer}>
      <div className={styles.leftPanel}>
        <div className={styles.floatingOrbs}>
          <div className={styles.orb1} />
          <div className={styles.orb2} />
        </div>
        <div style={{ position: 'relative', zIndex: 10 }}>
          <h1 className={styles.heroTitle}>Join GradSphere</h1>
          <p className={styles.heroDesc}>
            Start your journey today. Unlock personalized recommendations for welfare schemes,
            prepare with AI-powered mock interviews, and secure your files directly in DigiLocker.
          </p>
        </div>
      </div>
      <div className={styles.rightPanel}>
        <RegisterForm />
      </div>
    </div>
  );
};

export default RegisterPage;
