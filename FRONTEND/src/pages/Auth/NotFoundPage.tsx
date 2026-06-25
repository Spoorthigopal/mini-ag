import React from 'react';
import { Link } from 'react-router-dom';
import { HelpCircle } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: 'radial-gradient(circle at 50% 50%, #0d1224 0%, #070913 100%)',
        color: '#ffffff',
        fontFamily: "'Inter', sans-serif",
        textAlign: 'center',
        padding: '2rem',
      }}
    >
      <HelpCircle size={80} style={{ color: '#ff453a', marginBottom: '1.5rem', filter: 'drop-shadow(0 0 15px rgba(255, 69, 58, 0.4))' }} />
      <h1 style={{ fontSize: '3rem', fontWeight: 800, margin: '0 0 1rem 0' }}>404</h1>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 600, margin: '0 0 1.5rem 0', color: 'rgba(255, 255, 255, 0.8)' }}>
        Page Not Found
      </h2>
      <p style={{ maxWidth: '450px', lineHeight: 1.6, color: 'rgba(255, 255, 255, 0.5)', margin: '0 0 2.5rem 0' }}>
        The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.
      </p>
      <Link
        to="/"
        style={{
          background: 'linear-gradient(135deg, #0a84ff 0%, #0070c9 100%)',
          color: '#ffffff',
          textDecoration: 'none',
          padding: '0.875rem 2rem',
          borderRadius: '0.75rem',
          fontWeight: 600,
          boxShadow: '0 4px 14px rgba(10, 132, 255, 0.4)',
          transition: 'transform 0.2s, box-shadow 0.2s',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-1px)';
          e.currentTarget.style.boxShadow = '0 6px 20px rgba(10, 132, 255, 0.5)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'none';
          e.currentTarget.style.boxShadow = '0 4px 14px rgba(10, 132, 255, 0.4)';
        }}
      >
        Go Back Home
      </Link>
    </div>
  );
};

export default NotFoundPage;
