import React from 'react';
import styles from './internships.module.css';

interface FilterPanelProps {
  filters: {
    role: string[];
    location: string[];
    type: string[];
  };
  onChange: (filters: any) => void;
  onClear: () => void;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  onChange,
  onClear,
}) => {
  const handleSelectChange = (key: string, value: string) => {
    onChange({
      ...filters,
      [key]: value ? [value] : [],
    });
  };

  return (
    <div className={styles.filterPanel}>
      <div className={styles.filterHeader}>
        <h3 className={styles.filterTitle}>Filter Internships</h3>
        <button className={styles.clearBtn} onClick={onClear}>Clear All</button>
      </div>

      <div className={styles.filterGrid}>
        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Role / Domain</label>
          <select 
            className={styles.filterSelect}
            value={filters.role[0] || ''}
            onChange={(e) => handleSelectChange('role', e.target.value)}
          >
            <option value="">All Roles</option>
            <option value="Software Engineer">Software Engineer</option>
            <option value="Frontend Developer">Frontend Developer</option>
            <option value="Backend Developer">Backend Developer</option>
            <option value="Data Analyst">Data Analyst</option>
            <option value="Product Manager">Product Manager</option>
          </select>
        </div>

        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Location</label>
          <select 
            className={styles.filterSelect}
            value={filters.location[0] || ''}
            onChange={(e) => handleSelectChange('location', e.target.value)}
          >
            <option value="">All Locations</option>
            <option value="Remote">Remote</option>
            <option value="Bangalore">Bangalore</option>
            <option value="Mumbai">Mumbai</option>
            <option value="New Delhi">New Delhi</option>
            <option value="Hyderabad">Hyderabad</option>
          </select>
        </div>

        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Job Type</label>
          <select 
            className={styles.filterSelect}
            value={filters.type[0] || ''}
            onChange={(e) => handleSelectChange('type', e.target.value)}
          >
            <option value="">All Types</option>
            <option value="Full-time">Full-time</option>
            <option value="Part-time">Part-time</option>
            <option value="Contract">Contract</option>
          </select>
        </div>
      </div>
    </div>
  );
};

export default FilterPanel;
