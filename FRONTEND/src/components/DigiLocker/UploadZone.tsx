import React, { useState, useRef } from 'react';
import { useDispatch } from 'react-redux';
import { addDocument, setUploading } from '../../redux/slices/documentSlice';
import { Button } from '../Common/Button';
import styles from './digilocker.module.css';
import { UploadCloud, CheckCircle, FileText } from 'lucide-react';

const categories = ['Academic', 'Professional', 'Identity', 'Financial'] as const;
type Category = typeof categories[number];

export const UploadZone: React.FC = () => {
  const dispatch = useDispatch();
  const [file, setFile] = useState<File | null>(null);
  const [category, setCategory] = useState<Category>('Academic');
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setLocalUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = () => {
    if (!file) return;
    setLocalUploading(true);
    dispatch(setUploading(true));
    setUploadProgress(0);

    // Create a persistent object URL so the viewer can display the file
    const objectUrl = URL.createObjectURL(file);

    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setLocalUploading(false);
          const newDoc = {
            id: Math.random().toString(36).substring(7),
            name: file.name,
            type: file.name.split('.').pop() || 'pdf',
            size: file.size,
            uploadedAt: new Date().toISOString().split('T')[0],
            category,
            url: objectUrl,
          };
          dispatch(addDocument(newDoc));
          dispatch(setUploading(false));
          setFile(null);
          return 100;
        }
        return prev + 20;
      });
    }, 150);
  };


  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className={styles.uploadCard}>
      <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.125rem', fontWeight: 700 }}>Upload New Document</h3>
      <input
        ref={fileInputRef}
        type="file"
        style={{ display: 'none' }}
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
            <p className={styles.uploaderText}>Drag & drop a file here, or click to select</p>
            <p className={styles.uploaderSubtext}>Supports PDF, PNG, JPG, DOC up to 10MB</p>
          </>
        )}
      </div>

      <div className={styles.controls} style={{ marginTop: '1rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <label style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', color: 'rgba(255, 255, 255, 0.4)' }}>Category</label>
          <select
            className={styles.select}
            value={category}
            onChange={(e) => setCategory(e.target.value as Category)}
            style={{ width: '100%' }}
          >
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
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
          {uploading ? `Uploading ${uploadProgress}%` : 'Secure File'}
        </Button>
      </div>
    </div>
  );
};

export default UploadZone;
