import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../redux/store';
import { addDocument } from '../../redux/slices/documentSlice';
import UploadZone from './UploadZone';
import DocumentGrid from './DocumentGrid';
import styles from './digilocker.module.css';
import { Shield } from 'lucide-react';

const mockDocs = [
  {
    id: '1',
    name: 'semester_1_transcript.pdf',
    type: 'pdf',
    category: 'Academic' as const,
    size: 245000,
    uploadedAt: '2026-05-10',
    url: '#',
  },
  {
    id: '2',
    name: 'aadhaar_card.pdf',
    type: 'pdf',
    category: 'Identity' as const,
    size: 154000,
    uploadedAt: '2026-06-01',
    url: '#',
  },
  {
    id: '3',
    name: 'internship_offer_letter.pdf',
    type: 'pdf',
    category: 'Professional' as const,
    size: 312000,
    uploadedAt: '2026-06-15',
    url: '#',
  },
];

export const DocumentManagement: React.FC = () => {
  const dispatch = useDispatch();
  const { documents } = useSelector((state: RootState) => state.document);

  useEffect(() => {
    // Populate mock documents if empty
    if (documents.length === 0) {
      mockDocs.forEach((doc) => {
        dispatch(addDocument(doc));
      });
    }
  }, [dispatch, documents.length]);

  return (
    <div className={styles.container}>
      <div>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Shield style={{ color: '#ff9f0a' }} /> DigiLocker Vault
        </h2>
        <p style={{ color: 'rgba(255, 255, 255, 0.5)', margin: '0.25rem 0 0 0', fontSize: '0.9375rem' }}>
          Your secure, decentralized vault. All documents are AES-256 encrypted and stored on-chain.
        </p>
      </div>

      <UploadZone />
      
      <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '2rem', marginTop: '1rem' }}>
        <h3 style={{ margin: '0 0 1.25rem 0', fontSize: '1.25rem', fontWeight: 700 }}>Your Secured Files</h3>
        <DocumentGrid />
      </div>
    </div>
  );
};

export default DocumentManagement;
