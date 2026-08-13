import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import { deleteDocument as deleteDocumentAction, updateDocument } from '../../redux/slices/documentSlice';
import {
  downloadDocument,
  deleteDocument as apiDeleteDocument,
  viewDocument,
  renameDocument as apiRenameDocument,
  replaceDocument as apiReplaceDocument,
} from '../../services/digilockerService';
import DocumentCard from './DocumentCard';
import { LoadingSpinner } from '../Common/LoadingSpinner';
import { NoData } from '../Common/NoData';
import styles from './digilocker.module.css';
import { Search } from 'lucide-react';

export const DocumentGrid: React.FC = () => {
  const dispatch = useDispatch();
  const { documents, uploading, loading } = useSelector((state: RootState) => state.document);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [actionError, setActionError] = useState<string | null>(null);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  const handleDownload = async (docId: string, filename: string) => {
    setActionError(null);
    try {
      await downloadDocument(docId, filename);
    } catch (err: any) {
      setActionError(err?.response?.data?.detail || 'Download failed. Please try again.');
    }
  };

  const handleView = async (docId: string, filename: string) => {
    setActionError(null);
    try {
      await viewDocument(docId, filename);
    } catch (err: any) {
      setActionError(err?.response?.data?.detail || 'Could not open document for viewing.');
    }
  };

  const handleDelete = async (docId: string) => {
    if (!window.confirm('Are you sure you want to permanently delete this document? This action is irreversible.')) return;
    setActionError(null);
    try {
      await apiDeleteDocument(docId);
      dispatch(deleteDocumentAction(docId));
    } catch (err: any) {
      setActionError(err?.response?.data?.detail || 'Delete failed. Please try again.');
    }
  };

  const handleRename = async (docId: string, newName: string): Promise<boolean> => {
    setActionError(null);
    try {
      const updated = await apiRenameDocument(docId, newName);
      dispatch(updateDocument(updated));
      return true;
    } catch (err: any) {
      setActionError(err?.response?.data?.detail || 'Rename failed. Please try again.');
      return false;
    }
  };

  const handleReplace = async (docId: string, file: File): Promise<boolean> => {
    setActionError(null);
    try {
      const updated = await apiReplaceDocument(docId, file);
      dispatch(updateDocument(updated));
      return true;
    } catch (err: any) {
      setActionError(err?.response?.data?.detail || 'Replace failed. Please try again.');
      return false;
    }
  };

  // Filter by category
  const categoryDocs = documents.filter(
    (doc) => categoryFilter === 'All' || doc.category === categoryFilter
  );

  // Sort: documents matching search come first
  const sortedDocs = [...categoryDocs].sort((a, b) => {
    const aMatch = search && a.document_name.toLowerCase().includes(search.toLowerCase()) ? 1 : 0;
    const bMatch = search && b.document_name.toLowerCase().includes(search.toLowerCase()) ? 1 : 0;
    return bMatch - aMatch;
  });

  if (loading || uploading) return <LoadingSpinner />;

  if (!documents || documents.length === 0) {
    return (
      <NoData message="No documents uploaded yet. Secure your academic transcripts, certificates, or IDs above." />
    );
  }

  return (
    <div className={styles.container}>
      {/* Action Error Banner */}
      {actionError && (
        <div style={{
          background: 'rgba(255, 69, 58, 0.12)',
          border: '1px solid rgba(255, 69, 58, 0.3)',
          borderRadius: '0.5rem',
          padding: '0.625rem 1rem',
          color: '#ff453a',
          fontSize: '0.875rem',
          marginBottom: '1rem',
        }}>
          ⚠ {actionError}
        </div>
      )}

      <div className={styles.controls}>
        <div style={{ flex: 1, position: 'relative' }}>
          <Search
            size={18}
            style={{
              position: 'absolute', left: '12px', top: '50%',
              transform: 'translateY(-50%)', color: 'rgba(255, 255, 255, 0.4)',
            }}
          />
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
          <option value="certificates">Certificates</option>
          <option value="transcripts">Transcripts</option>
          <option value="documents">Documents</option>
          <option value="certificates_backup">Certificates Backup</option>
        </select>
      </div>

      {sortedDocs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'rgba(255, 255, 255, 0.4)' }}>
          <h3>No Documents Found</h3>
          <p>Try adjusting your search query or choosing a different category filter.</p>
        </div>
      ) : (
        <div className={styles.grid}>
          {sortedDocs.map((doc) => {
            const isHighlighted =
              search !== '' && doc.document_name.toLowerCase().includes(search.toLowerCase());
            const ext = doc.document_name.split('.').pop() || 'file';
            return (
              <DocumentCard
                key={doc.document_id}
                id={doc.document_id}
                name={doc.document_name}
                type={ext}
                uploadDate={doc.upload_date}
                size={doc.file_size}
                encrypted={true}
                isHighlighted={isHighlighted}
                onDownload={() => handleDownload(doc.document_id, doc.document_name)}
                onDelete={() => handleDelete(doc.document_id)}
                onView={() => handleView(doc.document_id, doc.document_name)}
                onRename={(newName) => handleRename(doc.document_id, newName)}
                onReplace={(file) => handleReplace(doc.document_id, file)}
              />
            );
          })}
        </div>
      )}
    </div>
  );
};

export default DocumentGrid;
