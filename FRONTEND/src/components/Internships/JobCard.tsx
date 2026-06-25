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
          <p className={styles.company}>{company}</p>
        </div>
        <div className={styles.matchBadge} style={{ background: match >= 80 ? 'rgba(48, 209, 88, 0.15)' : 'rgba(10, 132, 255, 0.15)', color: match >= 80 ? '#30d158' : '#0a84ff' }}>
          {match}% Match
        </div>
      </div>

      <div className={styles.detailsGrid}>
        <p className={styles.detailItem}>📍 {location}</p>
        <p className={styles.detailItem}>💰 {stipend}</p>
        <p className={styles.detailItem}>⭐ {rating.toFixed(1)} / 5</p>
      </div>

      <div className={styles.tags}>
        {tags.map((t) => (
          <Badge key={t} variant="info" size="sm">{t}</Badge>
        ))}
      </div>

      <p className={styles.description}>{description}</p>

      <div className={styles.actions}>
        <Button variant="secondary" onClick={openUrl} style={{ flex: 1 }}>
          View Details
        </Button>
        <Button variant="primary" onClick={openUrl} style={{ flex: 1 }}>
          Apply
        </Button>
      </div>
    </div>
  );
};

export default JobCard;
