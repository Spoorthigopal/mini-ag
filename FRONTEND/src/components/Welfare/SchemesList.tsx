import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import { setSchemes, setFilters } from '../../redux/slices/welfareSlice';
import SchemeCard from './SchemeCard';
import FilterPanel from './FilterPanel';
import styles from './welfare.module.css';
import { Search } from 'lucide-react';

const mockSchemes = [
  {
    id: '1',
    name: 'National Merit Scholarship Program',
    amount: '₹50,000 / year',
    eligibility: ['Undergraduate', 'General', 'Postgraduate'],
    provider: 'Government of India',
    deadline: '2026-10-31',
    category: 'Scholarship',
  },
  {
    id: '2',
    name: 'Post-Matric Financial Aid for SC/ST Students',
    amount: '₹25,000 / semester',
    eligibility: ['SC/ST', 'Undergraduate'],
    provider: 'State Government',
    deadline: '2026-09-15',
    category: 'Scholarship',
  },
  {
    id: '3',
    name: 'University Excellence Grant for Research',
    amount: '₹75,000',
    eligibility: ['Postgraduate', 'General'],
    provider: 'University Foundation',
    deadline: '2026-08-30',
    category: 'Grant',
  },
  {
    id: '4',
    name: 'Minority Student Subsidy Fund',
    amount: '₹15,000 / year',
    eligibility: ['Minority', 'Undergraduate', 'Postgraduate'],
    provider: 'Corporate CSR',
    deadline: '2026-12-01',
    category: 'Subsidy',
  },
];

export const SchemesList: React.FC = () => {
  const dispatch = useDispatch();
  const { schemes, filters } = useSelector((state: RootState) => state.welfare);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Populate mock schemes if empty
    if (schemes.length === 0) {
      dispatch(setSchemes(mockSchemes));
    }
  }, [dispatch, schemes.length]);

  const handleFilterChange = (newFilters: any) => {
    dispatch(setFilters(newFilters));
  };

  const handleClearFilters = () => {
    dispatch(setFilters({
      type: [],
      amountRange: [0, 100000],
      eligibility: [],
      deadline: '',
      provider: [],
    }));
    setSearchTerm('');
  };

  const handleApply = (id: string) => {
    alert(`Application submitted successfully for scheme ID: ${id}`);
  };

  // Filter schemes locally
  const filteredSchemes = schemes.filter((scheme) => {
    // Search term check
    if (searchTerm && !scheme.name.toLowerCase().includes(searchTerm.toLowerCase()) && 
        !(scheme.provider && scheme.provider.toLowerCase().includes(searchTerm.toLowerCase()))) {
      return false;
    }
    
    // Type/Category check
    if (filters.type.length > 0 && !filters.type.includes(scheme.category || '')) {
      return false;
    }

    // Eligibility check
    if (filters.eligibility.length > 0) {
      const matchesEligibility = scheme.eligibility.some(el => filters.eligibility.includes(el));
      if (!matchesEligibility) return false;
    }

    // Provider check
    if (filters.provider.length > 0 && scheme.provider && !filters.provider.includes(scheme.provider)) {
      return false;
    }

    // Deadline check
    if (filters.deadline && scheme.deadline && scheme.deadline > filters.deadline) {
      return false;
    }

    // Amount check (parsing numbers roughly)
    const amountNum = parseInt(scheme.amount.replace(/[^0-9]/g, ''), 10) || 0;
    if (amountNum < filters.amountRange[0] || amountNum > filters.amountRange[1]) {
      return false;
    }

    return true;
  });

  return (
    <div className={styles.container}>
      <div className={styles.searchBarContainer}>
        <input
          type="text"
          placeholder="Search schemes by name, provider, or keyword..."
          className={styles.searchBar}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <FilterPanel 
        filters={filters} 
        onChange={handleFilterChange} 
        onClear={handleClearFilters} 
      />

      {filteredSchemes.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'rgba(255, 255, 255, 0.4)' }}>
          <h3>No Schemes Match Your Criteria</h3>
          <p>Try clearing filters or adjusting your search query.</p>
        </div>
      ) : (
        <div className={styles.schemesGrid}>
          {filteredSchemes.map((scheme) => (
            <SchemeCard
              key={scheme.id}
              id={scheme.id}
              name={scheme.name}
              amount={scheme.amount}
              eligibility={scheme.eligibility}
              provider={scheme.provider}
              deadline={scheme.deadline}
              onApply={handleApply}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default SchemesList;
