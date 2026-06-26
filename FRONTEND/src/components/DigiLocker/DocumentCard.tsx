import React, { useState, useRef } from 'react';
import styles from './digilocker.module.css';
import { Button } from '../Common/Button';
import { Badge } from '../Common/Badge';
import { Eye, Edit2, Trash2, Download, Upload, Check, X } from 'lucide-react';

interface DocumentCardProps {
    id: string;
    name: string;
    type: string;
    uploadDate: string;
    size: number;
    url?: string;
    encrypted: boolean;
    isHighlighted: boolean;
    onDownload: () => void;
    onDelete: () => void;
    onRename: (newName: string) => void;
    onView: () => void;
    onUpdate: (file: File) => void;
}

const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
};

const DocumentCard: React.FC<DocumentCardProps> = ({
    name,
    type,
    uploadDate,
    size,
    url,
    encrypted,
    isHighlighted,
    onDownload,
    onDelete,
    onRename,
    onView,
    onUpdate,
}) => {
    const [isEditing, setIsEditing] = useState(false);
    const [newName, setNewName] = useState(name);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleRenameSubmit = () => {
        if (newName.trim() !== '') {
            onRename(newName.trim());
        } else {
            setNewName(name);
        }
        setIsEditing(false);
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            onUpdate(e.target.files[0]);
        }
    };

    const handleLocalDownload = () => {
        // If it's a mock url '#', create a dummy blob to demonstrate local download
        if (!url || url === '#') {
            const blob = new Blob(['Dummy document content for ' + name], { type: 'text/plain' });
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(downloadUrl);
        } else {
            // Real URL download
            const a = document.createElement('a');
            a.href = url;
            a.download = name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
        onDownload(); // Trigger any parent callback if needed
    };

    return (
        <div className={`${styles.docCard} ${isHighlighted ? styles.docCardHighlighted : ''}`}>
            {encrypted && (
                <div className={styles.encryptedBadge}>
                    Encrypted
                </div>
            )}
            
            <div className={styles.docInfo}>
                {isEditing ? (
                    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <input 
                            className={styles.renameInput} 
                            value={newName} 
                            onChange={(e) => setNewName(e.target.value)} 
                            onKeyDown={(e) => e.key === 'Enter' && handleRenameSubmit()}
                            autoFocus
                        />
                        <button className={styles.iconBtn} onClick={handleRenameSubmit}><Check size={16} color="#30d158" /></button>
                        <button className={styles.iconBtn} onClick={() => { setIsEditing(false); setNewName(name); }}><X size={16} color="#ff453a" /></button>
                    </div>
                ) : (
                    <h4 className={styles.docName} title={name}>{name}</h4>
                )}

                <p className={styles.docMeta}>
                    <span className={styles.docMetaSpan}>{type.toUpperCase()}</span>
                    <span className={styles.docMetaSpan}>•</span>
                    <span className={styles.docMetaSpan}>{formatSize(size)}</span>
                </p>

                <p className={styles.docMeta} style={{ marginTop: '0.25rem' }}>
                    Uploaded: {new Date(uploadDate).toLocaleDateString()}
                </p>
            </div>

            <div className={styles.docActionsGrid}>
                <button className={styles.actionIconButton} onClick={onView} title="View Document">
                    <Eye size={18} />
                </button>
                <button className={styles.actionIconButton} onClick={() => setIsEditing(true)} title="Rename Document">
                    <Edit2 size={18} />
                </button>
                <button className={styles.actionIconButton} onClick={() => fileInputRef.current?.click()} title="Update / Replace Document">
                    <Upload size={18} />
                </button>
                <button className={`${styles.actionIconButton} ${styles.downloadBtn}`} onClick={handleLocalDownload} title="Download Document">
                    <Download size={18} />
                </button>
                <button className={`${styles.actionIconButton} ${styles.deleteBtn}`} onClick={onDelete} title="Delete Document">
                    <Trash2 size={18} />
                </button>
            </div>
            
            <input 
                type="file" 
                style={{ display: 'none' }} 
                ref={fileInputRef} 
                onChange={handleFileChange} 
            />
        </div>
    );
};

export default DocumentCard;