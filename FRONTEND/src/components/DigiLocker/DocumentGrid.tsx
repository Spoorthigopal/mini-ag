import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import { deleteDocument } from '../../redux/slices/documentSlice';
import DocumentCard from './DocumentCard';
import { LoadingSpinner } from '../Common/LoadingSpinner';
import { NoData } from '../Common/NoData';
import styles from './digilocker.module.css';
import { Search } from 'lucide-react';

export const DocumentGrid: React.FC = () => {
  const dispatch = useDispatch();
  const { documents, uploading } = useSelector((state: RootState) => state.document);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  const handleDownload = (id: string) => {
    const doc = documents.find(d => d.id === id);
    if (doc && doc.url) {
      window.open(doc.url, '_blank');
    } else {
      alert(`Download link not available for document ID: ${id}`);
    }
  };

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this document? This action is irreversible.')) {
      dispatch(deleteDocument(id));
    }
  };

  const filteredDocs = documents.filter((doc) => {
    const matchesSearch = doc.name.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = categoryFilter === 'All' || doc.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  if (uploading) return <LoadingSpinner />;
  if (!documents || documents.length === 0) {
    return <NoData message="No documents uploaded yet. Secure your academic transcripts, certificates, or IDs above." />;
  }

  return (
    <div className={styles.container}>
      <div className={styles.controls}>
        <div style={{ flex: 1, position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'rgba(255, 255, 255, 0.4)' }} />
          <input
            type="text"
            placeholder="Search documents by name..."
            value={search}
            onChange={handleSearch}
            className={styles.search}
            style={{ paddingLeft: '2.5rem', width: '100%' }}
          />
        </div>
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className={styles.select}
        >
          <option value="All">All Categories</option>
          <option value="Academic">Academic</option>
          <option value="Professional">Professional</option>
          <option value="Identity">Identity</option>
          <option value="Financial">Financial</option>
        </select>
      </div>
      
      {filteredDocs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'rgba(255, 255, 255, 0.4)' }}>
          <h3>No Documents Match Your Search</h3>
          <p>Try adjusting your search query or choosing a different category filter.</p>
        </div>
      ) : (
        <div className={styles.grid}>
          {filteredDocs.map((doc) => (
            <DocumentCard
              key={doc.id}
              id={doc.id}
              name={doc.name}
              type={doc.type}
              uploadDate={doc.uploadedAt}
              size={doc.size}
              url={doc.url}
              encrypted={true}
              onDownload={handleDownload}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentGrid;
