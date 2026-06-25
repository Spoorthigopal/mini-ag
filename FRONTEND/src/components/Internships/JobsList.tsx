import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import { setJobs, setFilters } from '../../redux/slices/internshipSlice';
import JobCard from './JobCard';
import FilterPanel from './FilterPanel';
import styles from './internships.module.css';

const mockJobs = [
  {
    id: '1',
    company: 'TechCorp Solutions',
    role: 'Software Engineer Intern',
    location: 'Bangalore',
    stipend: '₹40,000 / month',
    rating: 4.5,
    match: 92,
    tags: ['React', 'TypeScript', 'Node.js'],
    description: 'Looking for a passionate Frontend-focused engineer to build modular dashboards and UI portals using modern React and Redux.',
    applicationUrl: 'https://www.linkedin.com/jobs/search/?keywords=Software+Engineer+Intern&location=Bangalore',
  },
  {
    id: '2',
    company: 'FinSphere Systems',
    role: 'Data Analyst Intern',
    location: 'Remote',
    stipend: '₹35,000 / month',
    rating: 4.2,
    match: 78,
    tags: ['Python', 'SQL', 'Tableau'],
    description: 'Analyze financial data trends, generate reports, and build interactive dashboards to help make business decisions.',
    applicationUrl: 'https://www.linkedin.com/jobs/search/?keywords=Data+Analyst+Intern&f_WT=2',
  },
  {
    id: '3',
    company: 'Innovate Digital',
    role: 'Backend Developer Intern',
    location: 'Mumbai',
    stipend: '₹30,000 / month',
    rating: 4.0,
    match: 85,
    tags: ['Python', 'Django', 'PostgreSQL'],
    description: 'Help develop robust backend APIs, database structures, and server microservices using Django and clean patterns.',
    applicationUrl: 'https://www.linkedin.com/jobs/search/?keywords=Backend+Developer+Intern&location=Mumbai',
  },
  {
    id: '4',
    company: 'PixelPerfect Web',
    role: 'Frontend Developer Intern',
    location: 'Hyderabad',
    stipend: '₹25,000 / month',
    rating: 4.7,
    match: 89,
    tags: ['React', 'CSS Modules', 'JavaScript'],
    description: 'Implement pixel-perfect user interfaces, animations, and responsive components using modern styling frameworks.',
    applicationUrl: 'https://www.linkedin.com/jobs/search/?keywords=Frontend+Developer+Intern&location=Hyderabad',
  },
];

export const JobsList: React.FC = () => {
  const dispatch = useDispatch();
  const { jobs, filters } = useSelector((state: RootState) => state.internship);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (jobs.length === 0) {
      dispatch(setJobs(mockJobs));
    }
  }, [dispatch, jobs.length]);

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
  };

  const handleApply = (id: string) => {
    // no-op: openUrl is handled inside JobCard
  };

  const filteredJobs = jobs.filter((job) => {
    if (searchTerm && !job.role.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !job.company.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }

    if (filters.role.length > 0 && !filters.role.includes(job.role.split(' ')[0] || '')) {
      // rough match for demonstration
      const matched = filters.role.some(r => job.role.toLowerCase().includes(r.toLowerCase()));
      if (!matched) return false;
    }

    if (filters.location.length > 0 && !filters.location.includes(job.location)) {
      return false;
    }

    return true;
  });

  return (
    <div className={styles.container}>
      <div style={{ display: 'flex', gap: '1rem', width: '100%' }}>
        <input
          type="text"
          placeholder="Search internships by role, company, or skills..."
          className={styles.chatInput}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <FilterPanel
        filters={filters}
        onChange={handleFilterChange}
        onClear={handleClearFilters}
      />

      {filteredJobs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'rgba(255, 255, 255, 0.4)' }}>
          <h3>No Internship Openings Match Your Selection</h3>
          <p>Clear filters or broaden your query to find more options.</p>
        </div>
      ) : (
        <div className={styles.jobsGrid}>
          {filteredJobs.map((job) => (
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
              jobUrl={(job as any).applicationUrl}
              onApply={handleApply}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default JobsList;
