import React from 'react';
import styles from './SchemeCard.module.css';
import { Button } from '../Common/Button';
import { Badge } from '../Common/Badge';

interface SchemeCardProps {
  id: string;
  name: string;
  amount: string;
  eligibility: string[];
  provider?: string;
  deadline?: string;
  icon?: React.ReactNode;
  applicationUrl?: string;
  onApply: (id: string, url?: string) => void;
}

export const SchemeCard: React.FC<SchemeCardProps> = ({
  id,
  name,
  amount,
  eligibility,
  provider,
  deadline,
  icon,
  applicationUrl,
  onApply,
}) => {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        {icon && <span className={styles.icon}>{icon}</span>}
        <h3 className={styles.title}>{name}</h3>
      </div>
      <p className={styles.amount}>Amount: <strong>{amount}</strong></p>
      <div className={styles.eligibility}>
        {eligibility.map((tag) => (
          <Badge key={tag} variant="info" size="sm">{tag}</Badge>
        ))}
      </div>
      {provider && <p className={styles.provider}>Provider: {provider}</p>}
      {deadline && <p className={styles.deadline}>Deadline: {deadline}</p>}
      <Button variant="primary" onClick={() => onApply(id, applicationUrl)} className={styles.applyBtn}>
        Apply Now
      </Button>
    </div>
  );
};

export default SchemeCard;
