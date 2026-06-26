import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import { setJobs, setFilters } from '../../redux/slices/internshipSlice';
import JobCard from './JobCard';
import FilterPanel from './FilterPanel';
import styles from './internships.module.css';
import api from '../../services/api';

export const JobsList: React.FC = () => {
  const dispatch = useDispatch();
  const { jobs, filters } = useSelector((state: RootState) => state.internship);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchJobs = async (query: string) => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get('/internships/search_live', {
        params: { query: query || 'internships in India', limit: 20 }
      });
      const fetchedJobs = res.data.map((job: any) => ({
        id: job.id || String(Math.random()),
        company: job.company_name || 'Unknown Company',
        role: job.job_title || 'Internship',
        location: job.location || 'Remote',
        type: job.job_type || 'Internship',
        stipend: job.stipend ? `₹${job.stipend}/month` : 'Unpaid / Not Disclosed',
        rating: Number(job.company_rating || (Math.random() * 2 + 3).toFixed(1)),
        match: Math.floor(Math.random() * 20 + 70), // Mocked match score
        tags: job.required_skills ? job.required_skills.slice(0, 3) : ['Internship'],
        description: job.job_description ? (job.job_description.slice(0, 150) + '...') : 'No description available.',
        applicationUrl: job.application_url,
      }));
      dispatch(setJobs(fetchedJobs));
    } catch (err) {
      console.error(err);
      setError('Failed to fetch jobs. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (jobs.length === 0) {
      fetchJobs('internships');
    }
  }, []);

  const handleFilterChange = (newFilters: any) => {
    dispatch(setFilters(newFilters));
  };

  const handleClearFilters = () => {
    dispatch(setFilters({
      role: [],
      location: [],
      type: [],
    }));
    setSearchTerm('');
    fetchJobs('internships');
  };

  const handleSearchSubmit = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      fetchJobs(searchTerm);
    }
  };

  const handleApply = (id: string) => {
    // openUrl handles redirection inside JobCard based on applicationUrl
  };

  const filteredJobs = jobs.filter((job: any) => {
    if (filters.role.length > 0 && !filters.role.includes(job.role.split(' ')[0] || '')) {
      const matched = filters.role.some((r: string) => job.role.toLowerCase().includes(r.toLowerCase()));
      if (!matched) return false;
    }

    if (filters.location.length > 0 && !filters.location.includes(job.location)) {
      return false;
    }

    if (filters.type && filters.type.length > 0 && !filters.type.includes(job.type)) {
      return false;
    }

    return true;
  });

  return (
    <div className={styles.container}>
      <div style={{ display: 'flex', gap: '1rem', width: '100%', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Search internships by role, company, or skills and press Enter..."
          className={styles.chatInput}
          style={{ flex: 1 }}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyDown={handleSearchSubmit}
        />
        <button 
          onClick={() => fetchJobs(searchTerm)} 
          style={{ padding: '0.75rem 1.5rem', background: '#0a84ff', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 600 }}
        >
          Search
        </button>
      </div>

      <FilterPanel
        filters={filters}
        onChange={handleFilterChange}
        onClear={handleClearFilters}
      />

      {error ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#ff453a' }}>
          <p>{error}</p>
        </div>
      ) : loading ? (
        <div className={styles.jobsGrid}>
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className={styles.skeletonCard} style={{ 
              background: 'rgba(255, 255, 255, 0.03)', 
              borderRadius: '1.5rem', 
              padding: '1.75rem', 
              height: '350px',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              animation: 'pulse 1.5s infinite ease-in-out'
            }}>
              <style>{`
                @keyframes pulse {
                  0% { opacity: 1; }
                  50% { opacity: 0.5; }
                  100% { opacity: 1; }
                }
              `}</style>
              <div style={{ height: '24px', width: '60%', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '4px', marginBottom: '12px' }} />
              <div style={{ height: '16px', width: '40%', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '4px', marginBottom: '24px' }} />
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '24px' }}>
                <div style={{ height: '36px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '8px' }} />
                <div style={{ height: '36px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '8px' }} />
                <div style={{ height: '36px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '8px' }} />
              </div>
              <div style={{ height: '12px', width: '90%', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '4px', marginBottom: '8px' }} />
              <div style={{ height: '12px', width: '70%', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '4px' }} />
            </div>
          ))}
        </div>
      ) : filteredJobs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'rgba(255, 255, 255, 0.4)' }}>
          <h3>No Internship Openings Match Your Selection</h3>
          <p>Clear filters or broaden your query to find more options.</p>
        </div>
      ) : (
        <div className={styles.jobsGrid}>
          {filteredJobs.map((job: any) => (
            <JobCard
              key={job.id}
              id={job.id}
              company={job.company}
              role={job.role}
              location={job.location}
              stipend={job.stipend}
              rating={job.rating}
              match={job.match}
              tags={job.tags}
              description={job.description}
              jobUrl={job.applicationUrl}
              onApply={handleApply}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default JobsList;
