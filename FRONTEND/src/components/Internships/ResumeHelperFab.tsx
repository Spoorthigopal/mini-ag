import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, X } from 'lucide-react';
import styles from './internships.module.css';

export const ResumeHelperFab: React.FC = () => {
  const navigate = useNavigate();
  const [showTooltip, setShowTooltip] = useState(false);

  const handleClick = () => {
    navigate('/internships/chat');
  };

  return (
    <div className={styles.resumeFabContainer}>
      {showTooltip && (
        <div className={styles.resumeFabTooltip}>
          <div className={styles.resumeFabTooltipContent}>
            <FileText size={16} style={{ color: '#30d158', flexShrink: 0 }} />
            <div>
              <div className={styles.resumeFabTooltipTitle}>Resume Helper</div>
              <div className={styles.resumeFabTooltipText}>AI-powered resume analysis &amp; career coaching</div>
            </div>
            <button
              className={styles.resumeFabTooltipClose}
              onClick={(e) => { e.stopPropagation(); setShowTooltip(false); }}
            >
              <X size={12} />
            </button>
          </div>
        </div>
      )}
      <button
        className={styles.resumeFab}
        onClick={handleClick}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        title="Open Resume Helper"
        aria-label="Open Resume Helper AI"
      >
        <FileText size={22} />
        <span className={styles.resumeFabPulse} />
      </button>
    </div>
  );
};

export default ResumeHelperFab;
