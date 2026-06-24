import React, { useState, ChangeEvent } from 'react';
import { useDispatch } from 'react-redux';
import { addDocument, setUploading } from '../../redux/slices/documentSlice';
import Button from '../../Common/Button';
import Input from '../../Common/Input';
import styles from './UploadZone.module.css';
import { v4 as uuidv4 } from 'uuid';

const categories = ['Academic', 'Professional', 'Identity', 'Financial'] as const;

type Category = typeof categories[number];

const UploadZone: React.FC = () => {
  const dispatch = useDispatch();
  const [file, setFile] = useState<File | null>(null);
  const [category, setCategory] = useState<Category>('Academic');
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setLocalUploading] = useState(false);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLocalUploading(true);
    dispatch(setUploading(true));
    // Simulate upload delay
    await new Promise((res) => setTimeout(res, 1500));
    const newDoc = {
      id: uuidv4(),
      name: file.name,
      type: file.type || 'application/octet-stream',
      size: file.size,
      uploadDate: new Date().toISOString(),
      category,
      url: URL.createObjectURL(file),
      encrypted: true,
    };
    dispatch(addDocument(newDoc));
    dispatch(setUploading(false));
    setLocalUploading(false);
    setFile(null);
  };

  return (
    <div className={styles.container}>
      <div
        className={${styles.dropzone} }
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={(e) => {
          e.preventDefault();
          setDragActive(false);
        }}
        onDrop={handleDrop}
      >
        {file ? (
          <p>{file.name}</p>
        ) : (
          <p>Drag & drop a file here, or click to select</p>
        )}
        <input
          type= file
          className={styles.fileInput}
          onChange={handleFileChange}
        />
      </div>
      <div className={styles.controls}>
        <select
          className={styles.select}
          value={category}
          onChange={(e) => setCategory(e.target.value as Category)}
        >
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <Button
          variant=primary
          disabled={!file || uploading}
          onClick={handleUpload}
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </Button>
      </div>
    </div>
  );
};

export default UploadZone;
