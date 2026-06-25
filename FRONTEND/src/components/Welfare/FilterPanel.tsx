import React from 'react';
import styles from './welfare.module.css';

interface FilterPanelProps {
  filters: {
    type: string[];
    amountRange: [number, number];
    eligibility: string[];
    deadline: string;
    provider: string[];
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

  const handleTextChange = (key: string, value: string) => {
    onChange({
      ...filters,
      [key]: value,
    });
  };

  return (
    <div className={styles.filterPanel}>
      <div className={styles.filterHeader}>
        <h3 className={styles.filterTitle}>Filter Schemes</h3>
        <button className={styles.clearBtn} onClick={onClear}>Clear All</button>
      </div>
      
      <div className={styles.filterGrid}>
        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Scheme Type</label>
          <select 
            className={styles.filterSelect}
            value={filters.type[0] || ''}
            onChange={(e) => handleSelectChange('type', e.target.value)}
          >
            <option value="">All Types</option>
            <option value="Scholarship">Scholarship</option>
            <option value="Grant">Grant</option>
            <option value="Subsidy">Subsidy</option>
            <option value="Loan">Loan</option>
          </select>
        </div>

        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Minimum Amount</label>
          <select 
            className={styles.filterSelect}
            value={filters.amountRange[0]}
            onChange={(e) => onChange({
              ...filters,
              amountRange: [Number(e.target.value), filters.amountRange[1]],
            })}
          >
            <option value="0">Any Amount</option>
            <option value="5000">₹5,000+</option>
            <option value="10000">₹10,000+</option>
            <option value="25000">₹25,000+</option>
            <option value="50000">₹50,000+</option>
          </select>
        </div>

        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Eligibility / Category</label>
          <select 
            className={styles.filterSelect}
            value={filters.eligibility[0] || ''}
            onChange={(e) => handleSelectChange('eligibility', e.target.value)}
          >
            <option value="">All Categories</option>
            <option value="Undergraduate">Undergraduate</option>
            <option value="Postgraduate">Postgraduate</option>
            <option value="SC/ST">SC/ST</option>
            <option value="OBC">OBC</option>
            <option value="Minority">Minority</option>
            <option value="General">General</option>
          </select>
        </div>

        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Provider</label>
          <select 
            className={styles.filterSelect}
            value={filters.provider[0] || ''}
            onChange={(e) => handleSelectChange('provider', e.target.value)}
          >
            <option value="">All Providers</option>
            <option value="Government of India">Government of India</option>
            <option value="State Government">State Government</option>
            <option value="University Foundation">University Foundation</option>
            <option value="Corporate CSR">Corporate CSR</option>
          </select>
        </div>

        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Deadline Before</label>
          <input 
            type="date"
            className={styles.filterSelect}
            value={filters.deadline}
            onChange={(e) => handleTextChange('deadline', e.target.value)}
          />
        </div>
      </div>
    </div>
  );
};

export default FilterPanel;
