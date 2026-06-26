import React from 'react';
import styles from './JobCard.module.css';
import { Button } from '../Common/Button';
import { Badge } from '../Common/Badge';

interface JobCardProps {
  id: string;
  company: string;
  role: string;
  location: string;
  stipend: string;
  rating: number;
  match: number;
  tags: string[];
  description: string;
  jobUrl?: string;
  onViewDetails?: (id: string) => void;
  onApply: (id: string) => void;
}

export const JobCard: React.FC<JobCardProps> = ({
  id,
  company,
  role,
  location,
  stipend,
  rating,
  match,
  tags,
  description,
  jobUrl,
  onViewDetails,
  onApply,
}) => {
  const openUrl = () => {
    if (jobUrl) {
      window.open(jobUrl, '_blank', 'noopener,noreferrer');
    } else {
      onViewDetails && onViewDetails(id);
    }
  };

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div className={styles.titleInfo}>
          <h3 className={styles.role}>{role}</h3>
          <p className={styles.company}>🏢 {company}</p>
        </div>
      </div>

      <div className={styles.detailsGrid}>
        <p className={styles.detailItem}>📍 {location}</p>
        <p className={styles.detailItem}>💰 {stipend}</p>
        <p className={styles.detailItem}>⭐ {rating.toFixed(1)} / 5</p>
      </div>

      <div className={styles.tags}>
        {tags.map((t) => (
          <span key={t} className={styles.tag}>{t}</span>
        ))}
      </div>

      <p className={styles.description}>{description}</p>

      <div className={styles.actions}>
        <button className={styles.btnSecondary} onClick={openUrl}>
          View Details
        </button>
        <button className={styles.btnPrimary} onClick={openUrl}>
          Apply Now 🚀
        </button>
      </div>
    </div>
  );
};

export default JobCard;
