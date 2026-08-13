import React, { useState, useRef } from 'react';
import { useDispatch } from 'react-redux';
import { addDocument, setUploading } from '../../redux/slices/documentSlice';
import { uploadDocument } from '../../services/digilockerService';
import { Button } from '../Common/Button';
import styles from './digilocker.module.css';
import { UploadCloud, FileText, CheckCircle, AlertCircle } from 'lucide-react';

// Backend-accepted categories
const BACKEND_CATEGORIES = ['certificates', 'transcripts', 'documents', 'certificates_backup'] as const;
type BackendCategory = typeof BACKEND_CATEGORIES[number];

const CATEGORY_LABELS: Record<BackendCategory, string> = {
  certificates: 'Certificates',
  transcripts: 'Transcripts',
  documents: 'Documents',
  certificates_backup: 'Certificates Backup',
};

export const UploadZone: React.FC = () => {
  const dispatch = useDispatch();
  const [file, setFile] = useState<File | null>(null);
  const [category, setCategory] = useState<BackendCategory>('certificates');
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setLocalUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const ALLOWED_TYPES = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/zip'];
  const ALLOWED_EXT = ['pdf', 'png', 'jpg', 'jpeg', 'docx', 'zip'];

  const validateFile = (f: File): string | null => {
    const ext = f.name.split('.').pop()?.toLowerCase() || '';
    if (!ALLOWED_EXT.includes(ext)) {
      return `File type ".${ext}" is not supported. Allowed: PDF, PNG, JPG, DOCX, ZIP`;
    }
    if (f.size > 50 * 1024 * 1024) {
      return 'File exceeds the 50 MB size limit.';
    }
    return null;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      const err = validateFile(f);
      if (err) { setErrorMsg(err); return; }
      setErrorMsg(null);
      setSuccessMsg(null);
      setFile(f);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const f = e.dataTransfer.files[0];
      const err = validateFile(f);
      if (err) { setErrorMsg(err); return; }
      setErrorMsg(null);
      setSuccessMsg(null);
      setFile(f);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLocalUploading(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    dispatch(setUploading(true));

    // Simulate progress while the real upload runs
    let fakeProgress = 0;
    const progressInterval = setInterval(() => {
      fakeProgress = Math.min(fakeProgress + 10, 85);
      setProgress(fakeProgress);
    }, 200);

    try {
      const newDoc = await uploadDocument(file, category, file.name);
      clearInterval(progressInterval);
      setProgress(100);

      // Add to Redux store so it appears in the grid immediately
      dispatch(addDocument(newDoc));
      setSuccessMsg(`"${file.name}" encrypted & secured successfully!`);
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err: any) {
      clearInterval(progressInterval);
      const detail = err?.response?.data?.detail || 'Upload failed. Please try again.';
      setErrorMsg(detail);
    } finally {
      setLocalUploading(false);
      dispatch(setUploading(false));
      setTimeout(() => setProgress(0), 1500);
    }
  };

  const triggerFileSelect = () => fileInputRef.current?.click();

  return (
    <div className={styles.uploadCard}>
      <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.125rem', fontWeight: 700 }}>
        Upload New Document
      </h3>

      <input
        ref={fileInputRef}
        type="file"
        style={{ display: 'none' }}
        accept=".pdf,.png,.jpg,.jpeg,.docx,.zip"
        onChange={handleFileChange}
      />

      <div
        className={`${styles.dropzone} ${dragActive ? styles.dropzoneActive : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={triggerFileSelect}
      >
        {file ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
            <FileText size={40} style={{ color: '#ff9f0a' }} />
            <p className={styles.uploaderText}>{file.name}</p>
            <p className={styles.uploaderSubtext}>{(file.size / 1024).toFixed(1)} KB</p>
          </div>
        ) : (
          <>
            <UploadCloud size={40} className={styles.uploaderIcon} />
            <p className={styles.uploaderText}>Drag &amp; drop a file here, or click to select</p>
            <p className={styles.uploaderSubtext}>Supports PDF, PNG, JPG, DOCX, ZIP · Max 50 MB</p>
          </>
        )}
      </div>

      {/* Upload Progress Bar */}
      {uploading && (
        <div style={{ marginTop: '0.75rem' }}>
          <div style={{
            height: '4px',
            borderRadius: '2px',
            background: 'rgba(255, 255, 255, 0.1)',
            overflow: 'hidden',
          }}>
            <div style={{
              height: '100%',
              width: `${progress}%`,
              background: 'linear-gradient(90deg, #ff9f0a, #ff6b00)',
              borderRadius: '2px',
              transition: 'width 0.2s ease',
            }} />
          </div>
          <p style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.5)', marginTop: '0.375rem', textAlign: 'right' }}>
            Encrypting &amp; uploading… {progress}%
          </p>
        </div>
      )}

      {/* Success Message */}
      {successMsg && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '0.5rem',
          background: 'rgba(48, 209, 88, 0.12)',
          border: '1px solid rgba(48, 209, 88, 0.3)',
          borderRadius: '0.5rem',
          padding: '0.625rem 0.875rem',
          marginTop: '0.75rem',
          color: '#30d158',
          fontSize: '0.875rem',
        }}>
          <CheckCircle size={16} />
          {successMsg}
        </div>
      )}

      {/* Error Message */}
      {errorMsg && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '0.5rem',
          background: 'rgba(255, 69, 58, 0.12)',
          border: '1px solid rgba(255, 69, 58, 0.3)',
          borderRadius: '0.5rem',
          padding: '0.625rem 0.875rem',
          marginTop: '0.75rem',
          color: '#ff453a',
          fontSize: '0.875rem',
        }}>
          <AlertCircle size={16} />
          {errorMsg}
        </div>
      )}

      <div className={styles.controls} style={{ marginTop: '1rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <label style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: 'rgba(255, 255, 255, 0.4)' }}>
            Category
          </label>
          <select
            className={styles.select}
            value={category}
            onChange={(e) => setCategory(e.target.value as BackendCategory)}
            style={{ width: '100%' }}
          >
            {BACKEND_CATEGORIES.map((c) => (
              <option key={c} value={c}>{CATEGORY_LABELS[c]}</option>
            ))}
          </select>
        </div>

        <Button
          variant="primary"
          disabled={!file || uploading}
          onClick={handleUpload}
          style={{
            alignSelf: 'flex-end',
            height: '2.75rem',
            background: 'linear-gradient(135deg, #ff9f0a 0%, #ff8000 100%)',
            border: 'none',
            color: '#ffffff',
          }}
        >
          {uploading ? `Encrypting… ${progress}%` : 'Secure File'}
        </Button>
      </div>
    </div>
  );
};

export default UploadZone;
