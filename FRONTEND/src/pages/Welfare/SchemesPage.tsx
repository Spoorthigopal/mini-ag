import React from 'react';
import SchemesList from '../../components/Welfare/SchemesList';
import SchemeAssistChatbot from '../../components/Welfare/SchemeAssistChatbot';

export const SchemesPage: React.FC = () => {
  return (
    <div style={{ position: 'relative' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0 }}>Welfare &amp; Financial Aid Schemes</h2>
        <p style={{ color: 'rgba(255, 255, 255, 0.5)', margin: '0.25rem 0 0 0', fontSize: '0.9375rem' }}>
          Browse available scholarships, grants, and subsidies from the university and governmental agencies.
        </p>
      </div>
      <SchemesList />
      <SchemeAssistChatbot />
    </div>
  );
};

export default SchemesPage;
