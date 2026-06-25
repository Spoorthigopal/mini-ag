import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer
      style={{
        marginTop: 'auto',
        padding: '2rem 0 1rem 0',
        textAlign: 'center',
        fontSize: '0.8125rem',
        color: 'rgba(255, 255, 255, 0.4)',
        borderTop: '1px solid rgba(255, 255, 255, 0.05)',
      }}
    >
      <p style={{ margin: 0 }}>
        &copy; {new Date().getFullYear()} STU-MINI. All rights reserved.
      </p>
    </footer>
  );
};

export default Footer;
