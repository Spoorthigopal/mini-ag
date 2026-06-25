import React from 'react';
import styles from './interview.module.css';
import { Briefcase, ArrowRight } from 'lucide-react';

export interface JobOption {
  id: string;
  title: string;
  company: string;
  description: string;
}

const jobOptions: JobOption[] = [
  {
    id: '1',
    title: 'Software Engineer Intern',
    company: 'TechCorp Solutions',
    description: 'HTML/CSS, React, TypeScript, Redux Toolkit, front-end development, mock coding challenges.',
  },
  {
    id: '2',
    title: 'Data Analyst Intern',
    company: 'FinSphere Systems',
    description: 'Python, SQL databases, data cleaning, data visualization, basic statistical modeling.',
  },
  {
    id: '3',
    title: 'Backend Developer Intern',
    company: 'Innovate Digital',
    description: 'Python backend web frameworks (Django/Flask), SQL databases, REST API design.',
  },
];

interface JobSelectorProps {
  selectedJobId: string | null;
  onSelect: (job: JobOption) => void;
  onStart: () => void;
}

export const JobSelector: React.FC<JobSelectorProps> = ({
  selectedJobId,
  onSelect,
  onStart,
}) => {
  return (
    <div className={styles.selectorCard}>
      <h3 className={styles.selectorTitle}>Select a Job Role for Mock Interview</h3>
      <div className={styles.jobGrid}>
        {jobOptions.map((job) => (
          <button
            key={job.id}
            className={`${styles.jobSelectItem} ${selectedJobId === job.id ? styles.jobSelectActive : ''}`}
            onClick={() => onSelect(job)}
          >
            <Briefcase size={20} style={{ color: selectedJobId === job.id ? '#0a84ff' : 'rgba(255, 255, 255, 0.4)', marginBottom: '0.75rem' }} />
            <h4 className={styles.jobRole}>{job.title}</h4>
            <p className={styles.jobCompany}>{job.company}</p>
            <p style={{ fontSize: '0.8125rem', color: 'rgba(255, 255, 255, 0.4)', marginTop: '0.5rem', lineHeight: '1.4' }}>
              {job.description}
            </p>
          </button>
        ))}
      </div>

      <button
        onClick={onStart}
        disabled={!selectedJobId}
        style={{
          background: selectedJobId ? 'linear-gradient(135deg, #0a84ff 0%, #0070c9 100%)' : 'rgba(255, 255, 255, 0.05)',
          color: selectedJobId ? '#ffffff' : 'rgba(255, 255, 255, 0.3)',
          border: 'none',
          padding: '0.875rem 2rem',
          borderRadius: '0.75rem',
          fontWeight: 600,
          cursor: selectedJobId ? 'pointer' : 'not-allowed',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.5rem',
          transition: 'all 0.2s',
          alignSelf: 'flex-end',
          marginTop: '1rem',
        }}
      >
        Start Session <ArrowRight size={18} />
      </button>
    </div>
  );
};

export default JobSelector;
