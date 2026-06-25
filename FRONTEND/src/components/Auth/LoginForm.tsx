import React, { useState } from 'react';
import styles from './auth.module.css';
import { useAuth } from '../../hooks/useAuth';
import { Loader2, Mail, Lock } from 'lucide-react';
import { Link } from 'react-router-dom';

export const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);
  
  const { login, error: authError } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (!email || !password) {
      setValidationError('Please fill in all fields.');
      return;
    }

    if (!/\S+@\S+\.\S+/.test(email)) {
      setValidationError('Please enter a valid email address.');
      return;
    }

    setIsSubmitting(true);
    await login(email, password);
    setIsSubmitting(false);
  };

  const displayError = validationError || authError;

  return (
    <div className={styles.authCard}>
      <h2 className={styles.title}>Welcome Back</h2>
      <p className={styles.subtitle}>Sign in to your GradSphere account</p>

      {displayError && (
        <div className={styles.error} style={{ marginBottom: '1.25rem', padding: '0.75rem', background: 'rgba(255, 69, 58, 0.1)', borderRadius: '0.5rem' }}>
          {displayError}
        </div>
      )}

      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.inputGroup}>
          <label className={styles.label} htmlFor="email">Email Address</label>
          <div style={{ position: 'relative' }}>
            <Mail size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'rgba(255, 255, 255, 0.4)' }} />
            <input
              id="email"
              type="email"
              placeholder="you@university.edu"
              className={styles.input}
              style={{ paddingLeft: '2.5rem' }}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isSubmitting}
            />
          </div>
        </div>

        <div className={styles.inputGroup}>
          <label className={styles.label} htmlFor="password">Password</label>
          <div style={{ position: 'relative' }}>
            <Lock size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'rgba(255, 255, 255, 0.4)' }} />
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              className={styles.input}
              style={{ paddingLeft: '2.5rem' }}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isSubmitting}
            />
          </div>
        </div>

        <button type="submit" className={styles.submitBtn} disabled={isSubmitting}>
          {isSubmitting ? (
            <>
              <Loader2 size={18} className="spin" style={{ animation: 'spin 1s linear infinite' }} />
              Signing In...
            </>
          ) : (
            'Sign In'
          )}
        </button>
      </form>

      <p className={styles.footerText}>
        Don't have an account?{' '}
        <Link to="/register" className={styles.link}>
          Sign Up
        </Link>
      </p>
    </div>
  );
};

export default LoginForm;
