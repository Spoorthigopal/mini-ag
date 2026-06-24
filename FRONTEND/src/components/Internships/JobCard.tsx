import React from " react\;
import styles from \./JobCard.module.css\;
import Button from \../../Common/Button\;
import Badge from \../../Common/Badge\;

interface JobCardProps {
 id: string;
 company: string;
 role: string;
 location: string;
 stipend: string;
 rating: number;
 match: number; // percentage
 tags: string[];
 description: string;
 onViewDetails: (id: string) => void;
 onApply: (id: string) => void;
}

const JobCard: React.FC<JobCardProps> = ({
 id,
 company,
 role,
 location,
 stipend,
 rating,
 match,
 tags,
 description,
 onViewDetails,
 onApply,
}) => (
 <div className={styles.card}>
 <div className={styles.header}>
 <h3 className={styles.role}>{role}</h3>
 <p className={styles.company}>{company}</p>
 </div>
 <p className={styles.location}>?? {location}</p>
 <p className={styles.stipend}>?? {stipend}</p>
 <div className={styles.rating}>? {rating.toFixed(1)} / 5</div>
 <div className={styles.match}>Match: {match}%</div>
 <div className={styles.tags}>
 {tags.map((t) => (
 <Badge key={t} variant=\cyan\ size=\sm\>{t}</Badge>
 ))}
 </div>
 <p className={styles.description}>{description}</p>
 <div className={styles.actions}>
 <Button variant=\secondary\ onClick={() => onViewDetails(id)}>View Details</Button>
 <Button variant=\primary\ onClick={() => onApply(id)}>Apply</Button>
 </div>
 </div>
);

export default JobCard;
