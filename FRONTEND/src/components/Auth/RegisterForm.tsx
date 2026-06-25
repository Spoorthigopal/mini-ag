import React, { useState } from 'react';
import styles from './auth.module.css';
import { useAuth } from '../../hooks/useAuth';
import { Loader2, Mail, Lock, UserPlus } from 'lucide-react';
import { Link } from 'react-router-dom';

export const RegisterForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);
  
  const { register, error: authError } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (!email || !password || !confirmPassword) {
      setValidationError('Please fill in all fields.');
      return;
    }

    if (!/\S+@\S+\.\S+/.test(email)) {
      setValidationError('Please enter a valid email address.');
      return;
    }

    if (password.length < 6) {
      setValidationError('Password must be at least 6 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setValidationError('Passwords do not match.');
      return;
    }

    setIsSubmitting(true);
    await register(email, password);
    setIsSubmitting(false);
  };

  const displayError = validationError || authError;

  return (
    <div className={styles.authCard}>
      <h2 className={styles.title}>Create Account</h2>
      <p className={styles.subtitle}>Get started with STU-MINI platform</p>

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

        <div className={styles.inputGroup}>
          <label className={styles.label} htmlFor="confirmPassword">Confirm Password</label>
          <div style={{ position: 'relative' }}>
            <Lock size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'rgba(255, 255, 255, 0.4)' }} />
            <input
              id="confirmPassword"
              type="password"
              placeholder="••••••••"
              className={styles.input}
              style={{ paddingLeft: '2.5rem' }}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={isSubmitting}
            />
          </div>
        </div>

        <button type="submit" className={styles.submitBtn} disabled={isSubmitting}>
          {isSubmitting ? (
            <>
              <Loader2 size={18} className="spin" style={{ animation: 'spin 1s linear infinite' }} />
              Creating Account...
            </>
          ) : (
            'Create Account'
          )}
        </button>
      </form>

      <p className={styles.footerText}>
        Already have an account?{' '}
        <Link to="/login" className={styles.link}>
          Sign In
        </Link>
      </p>
    </div>
  );
};

export default RegisterForm;
