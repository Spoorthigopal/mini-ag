import React from 'react';
import WelfareChat from '../../components/Welfare/WelfareChat';

export const ChatPage: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0 }}>Welfare Assistant Chat</h2>
        <p style={{ color: 'rgba(255, 255, 255, 0.5)', margin: '0.25rem 0 0 0', fontSize: '0.9375rem' }}>
          Get instant recommendations for scholarships, eligibility checking, and application assistance from our AI.
        </p>
      </div>
      <WelfareChat />
    </div>
  );
};

export default ChatPage;
