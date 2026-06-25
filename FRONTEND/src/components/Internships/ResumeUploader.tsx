import React, { useState, useRef } from 'react';
import styles from './internships.module.css';
import { UploadCloud, CheckCircle, FileText } from 'lucide-react';

interface ResumeUploaderProps {
  onUploadSuccess: (fileName: string, parsedData: any) => void;
}

export const ResumeUploader: React.FC<ResumeUploaderProps> = ({ onUploadSuccess }) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const simulateUpload = (name: string) => {
    setUploading(true);
    setFileName(name);
    setUploadProgress(0);

    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setUploading(false);
          onUploadSuccess(name, {
            skills: ['React', 'TypeScript', 'Node.js', 'Python'],
            experience: '1 year frontend experience',
          });
          return 100;
        }
        return prev + 10;
      });
    }, 150);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      simulateUpload(file.name);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      simulateUpload(file.name);
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className={styles.uploaderCard}>
      <input
        ref={fileInputRef}
        type="file"
        style={{ display: 'none' }}
        accept=".pdf,.doc,.docx"
        onChange={handleFileChange}
      />
      <div
        className={`${styles.dropzone} ${isDragActive ? styles.dropzoneActive : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={triggerFileSelect}
      >
        {fileName && uploadProgress === 100 ? (
          <div className={styles.successMessage}>
            <CheckCircle size={48} />
            <p className={styles.uploaderText}>Resume Uploaded Successfully!</p>
            <p className={styles.uploaderSubtext}>
              <FileText size={14} style={{ verticalAlign: 'middle', marginRight: '4px' }} />
              {fileName}
            </p>
          </div>
        ) : uploading ? (
          <div className={styles.progressContainer}>
            <div className={styles.progressLabel}>
              <span>Uploading resume...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className={styles.progressBar}>
              <div className={styles.progressFill} style={{ width: `${uploadProgress}%` }}></div>
            </div>
          </div>
        ) : (
          <>
            <UploadCloud size={48} className={styles.uploaderIcon} />
            <p className={styles.uploaderText}>Drag & Drop your Resume here</p>
            <p className={styles.uploaderSubtext}>Supports PDF, DOC, DOCX up to 5MB (Or click to browse)</p>
          </>
        )}
      </div>
    </div>
  );
};

export default ResumeUploader;
