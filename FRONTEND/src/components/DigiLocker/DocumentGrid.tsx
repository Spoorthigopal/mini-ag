import React, { useState, ChangeEvent } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import DocumentCard from './DocumentCard';
import LoadingSpinner from '../../Common/LoadingSpinner';
import NoData from '../../Common/NoData';
import styles from './DocumentGrid.module.css';

const DocumentGrid: React.FC = () => {
  const { documents, uploading } = useSelector((state: RootState) => ({
    documents: state.document.documents || [],
    uploading: state.document.uploading || false,
  }));
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');

  const handleSearch = (e: ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  const filteredDocs = documents.filter((doc) => {
    const matchesSearch = doc.name.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = categoryFilter === 'All' || doc.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  if (uploading) return <LoadingSpinner />;
  if (!documents.length) return <NoData message= No documents uploaded yet. />;

  return (
    <div className={styles.container}>
      <div className={styles.controls}>
        <input
          type=text
          placeholder=Search documents...
          value={search}
          onChange={handleSearch}
          className={styles.search}
        />
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className={styles.select}
        >
          <option value=All>All Categories</option>
          <option value=Academic>Academic</option>
          <option value=Professional>Professional</option>
          <option value=Identity>Identity</option>
          <option value=Financial>Financial</option>
        </select>
      </div>
      <div className={styles.grid}>
        {filteredDocs.map((doc) => (
          <DocumentCard
            key={doc.id}
            name={doc.name}
            type={doc.type}
            uploadDate={doc.uploadedAt}
            size={doc.size}
            url={doc.url}
            encrypted={doc.encrypted}
            onDownload={() => window.open(doc.url || '#')}
            onDelete={() => {/* dispatch delete action here if needed */}}
          />
        ))}
      </div>
    </div>
  );
};

export default DocumentGrid;
