import React, { useEffect, useState, useMemo } from 'react';
import SchemeCard from './SchemeCard';
import FilterPanel from './FilterPanel';
import styles from './welfare.module.css';
import api from '../../services/api';

interface Scheme {
  id: string;
  name: string;
  description: string;
  category: string;
  scheme_type: string;
  provider: string;
  states: string;
  tags: string;
  application_url: string;
  amount?: string;
  deadline?: string;
  eligibility?: string[];
}

const defaultFilters = {
  type: [] as string[],
  amountRange: [0, 100000] as [number, number],
  eligibility: [] as string[],
  deadline: '',
  provider: [] as string[],
};

export const SchemesList: React.FC = () => {
  const [allSchemes, setAllSchemes] = useState<Scheme[]>([]);
  const [filters, setFilters] = useState(defaultFilters);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const res = await api.get('/welfare/all');
        setAllSchemes(res.data);
      } catch (e) {
        setError('Could not load schemes. Make sure the backend is running.');
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const handleApply = (id: string, url?: string) => {
    if (url && url.trim() !== '') {
      window.open(url, '_blank', 'noopener,noreferrer');
      return;
    }
    // Extract OFFICIAL WEBSITE from description text as fallback
    const scheme = allSchemes.find(s => s.id === id);
    const text = scheme?.description || '';
    const match = text.match(/OFFICIAL WEBSITE:\s*(https?:\/\/[^\s\n]+)/);
    if (match && match[1]) {
      window.open(match[1].trim(), '_blank', 'noopener,noreferrer');
    }
  };

  const filteredSchemes = useMemo(() => {
    return allSchemes.filter(scheme => {
      // 1. Search Term
      if (searchTerm) {
        const q = searchTerm.toLowerCase();
        if (
          !(scheme.name || '').toLowerCase().includes(q) &&
          !(scheme.provider || '').toLowerCase().includes(q) &&
          !(scheme.tags || '').toLowerCase().includes(q)
        ) return false;
      }
      
      // 2. Type Filter
      if (filters.type.length > 0 && !filters.type.some(t =>
        (scheme.scheme_type || '').toLowerCase().includes(t.toLowerCase()) ||
        (scheme.category || '').toLowerCase().includes(t.toLowerCase())
      )) return false;
      
      // 3. Provider Filter
      if (filters.provider.length > 0 && !filters.provider.some(p =>
        (scheme.provider || '').toLowerCase().includes(p.toLowerCase())
      )) return false;
      
      // 4. Eligibility Filter
      if (filters.eligibility.length > 0 && !filters.eligibility.some(e =>
        (scheme.eligibility || []).some(el => el.toLowerCase().includes(e.toLowerCase())) ||
        (scheme.category || '').toLowerCase().includes(e.toLowerCase())
      )) return false;
      
      // 5. Amount Range
      if (filters.amountRange[0] > 0) {
        // basic parser: remove non-digits
        const numStr = (scheme.amount || '').replace(/[^0-9]/g, '');
        const amount = parseInt(numStr, 10);
        if (isNaN(amount) || amount < filters.amountRange[0]) return false;
      }
      
      // 6. Deadline Filter
      if (filters.deadline) {
        if (!scheme.deadline || scheme.deadline.toLowerCase() === 'ongoing') {
          // If no deadline or ongoing, maybe keep it. But if user wants before X, maybe reject?
          // Let's assume missing deadline is rejected if filter is set.
          return false;
        }
        // basic string comparison (assumes YYYY-MM-DD or parseable dates)
        // Since dates in JSON might be messy, we do a simple Date parse
        const filterDate = new Date(filters.deadline).getTime();
        const schemeDate = new Date(scheme.deadline).getTime();
        if (!isNaN(filterDate) && !isNaN(schemeDate)) {
          if (schemeDate > filterDate) return false;
        }
      }

      return true;
    });
  }, [allSchemes, searchTerm, filters]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem', color: 'rgba(255,255,255,0.5)' }}>
        <p>Loading schemes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', color: '#ff2d55' }}>
        <p>{error}</p>
      </div>
    );
  }

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
        onChange={setFilters}
        onClear={() => { setFilters(defaultFilters); setSearchTerm(''); }}
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
              amount={scheme.amount || 'See details'}
              eligibility={scheme.eligibility || [scheme.scheme_type]}
              provider={scheme.provider}
              deadline={scheme.deadline}
              applicationUrl={scheme.application_url}
              onApply={handleApply}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default SchemesList;
