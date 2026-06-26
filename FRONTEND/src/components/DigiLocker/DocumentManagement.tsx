import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import { setDocuments, setLoading, setError, clearAll } from '../../redux/slices/documentSlice';
import { listDocuments } from '../../services/digilockerService';
import UploadZone from './UploadZone';
import DocumentGrid from './DocumentGrid';
import styles from './digilocker.module.css';
import { Shield } from 'lucide-react';

export const DocumentManagement: React.FC = () => {
  const dispatch = useDispatch();
  const { error } = useSelector((state: RootState) => state.document);
  const { token } = useSelector((state: RootState) => state.auth);

  // Fetch the user's real documents from the backend on mount (and when token changes)
  useEffect(() => {
    if (!token) return;

    const fetchDocuments = async () => {
      dispatch(setLoading(true));
      dispatch(setError(null));
      try {
        const response = await listDocuments(undefined, 1, 50);
        dispatch(setDocuments(response.documents));
      } catch (err: any) {
        const msg =
          err?.response?.data?.detail ||
          'Failed to load documents. Please try again.';
        dispatch(setError(msg));
      } finally {
        dispatch(setLoading(false));
      }
    };

    fetchDocuments();

    // Clear documents on unmount to avoid stale state between user sessions
    return () => {
      dispatch(clearAll());
    };
  }, [dispatch, token]);

  return (
    <div className={styles.container}>
      <div>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Shield style={{ color: '#ff9f0a' }} /> DigiLocker Vault
        </h2>
        <p style={{ color: 'rgba(255, 255, 255, 0.5)', margin: '0.25rem 0 0 0', fontSize: '0.9375rem' }}>
          Your secure, encrypted vault. All documents are AES-256-GCM encrypted and only decryptable by you.
        </p>
      </div>

      {error && (
        <div style={{
          background: 'rgba(255, 69, 58, 0.15)',
          border: '1px solid rgba(255, 69, 58, 0.35)',
          borderRadius: '0.75rem',
          padding: '0.875rem 1.25rem',
          color: '#ff453a',
          fontSize: '0.9rem',
        }}>
          ⚠ {error}
        </div>
      )}

      <UploadZone />

      <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '2rem', marginTop: '1rem' }}>
        <h3 style={{ margin: '0 0 1.25rem 0', fontSize: '1.25rem', fontWeight: 700 }}>Your Secured Files</h3>
        <DocumentGrid />
      </div>
    </div>
  );
};

export default DocumentManagement;
