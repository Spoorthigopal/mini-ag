import React from 'react';
import JobsList from '../../components/Internships/JobsList';

export const JobsPage: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0 }}>Internships & Job Openings</h2>
        <p style={{ color: 'rgba(255, 255, 255, 0.5)', margin: '0.25rem 0 0 0', fontSize: '0.9375rem' }}>
          Explore professional internships and full-time opportunities. Optimize your match score by uploading your resume.
        </p>
      </div>
      <JobsList />
    </div>
  );
};

export default JobsPage;
