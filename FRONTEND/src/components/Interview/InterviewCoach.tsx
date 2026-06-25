import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import { startSession, clearInterview } from '../../redux/slices/interviewSlice';
import JobSelector, { JobOption } from './JobSelector';
import MockInterview from './MockInterview';
import { Card } from '../Common/Card';
import { Button } from '../Common/Button';
import styles from './interview.module.css';
import { Sparkles, RefreshCw } from 'lucide-react';

export const InterviewCoach: React.FC = () => {
  const dispatch = useDispatch();
  const { currentJob, isActive, feedback } = useSelector((state: RootState) => state.interview);
  const [selectedJob, setSelectedJobState] = React.useState<JobOption | null>(null);

  const handleSelectJob = (job: JobOption) => {
    setSelectedJobState(job);
  };

  const handleStart = () => {
    if (selectedJob) {
      dispatch(startSession({
        sessionId: Math.random().toString(36).substring(7),
        job: {
          id: selectedJob.id,
          title: selectedJob.title,
          company: selectedJob.company,
          description: selectedJob.description,
        },
      }));
    }
  };

  const handleReset = () => {
    dispatch(clearInterview());
    setSelectedJobState(null);
  };

  return (
    <div className={styles.container}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles style={{ color: '#0a84ff' }} /> AI Interview Coach
          </h2>
          <p style={{ color: 'rgba(255, 255, 255, 0.5)', margin: '0.25rem 0 0 0', fontSize: '0.9375rem' }}>
            Select a targeted job role to start a real-time simulated AI interview and receive detailed evaluations.
          </p>
        </div>

        {(isActive || feedback) && (
          <Button variant="danger" onClick={handleReset} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <RefreshCw size={16} /> Reset Session
          </Button>
        )}
      </div>

      {!isActive && !feedback ? (
        <JobSelector
          selectedJobId={selectedJob?.id || null}
          onSelect={handleSelectJob}
          onStart={handleStart}
        />
      ) : (
        <MockInterview />
      )}
    </div>
  );
};

export default InterviewCoach;
