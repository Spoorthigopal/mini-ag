import React from 'react';
import styles from './digilocker.module.css';
import Button from '../Common/Button';
import Badge from '../Common/Badge';

interface DocumentCardProps {
    name: string;
    type: string;
    uploadDate: string;
    size: number;
    url?: string;
    encrypted: boolean;
    onDownload: () => void;
    onDelete: () => void;
}

const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;

    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }

    if (bytes < 1024 * 1024 * 1024) {
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }

    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
};

const DocumentCard: React.FC<DocumentCardProps> = ({
    name,
    type,
    uploadDate,
    size,
    url,
    encrypted,
    onDownload,
    onDelete,
}) => {
    return (
        <div className={styles.card}>
            <div className={styles.info}>
                <h4 className={styles.name}>{name}</h4>

                <p className={styles.meta}>
                    Type: {type} • Size: {formatSize(size)}
                </p>

                <p className={styles.date}>
                    Uploaded:{' '}
                    {new Date(uploadDate).toLocaleDateString()}
                </p>
            </div>

            <div className={styles.actions}>
                {encrypted && (
                    <Badge variant="cyan" size="sm">
                        Encrypted
                    </Badge>
                )}

                <Button
                    variant="secondary"
                    onClick={onDownload}
                    disabled={!url}
                >
                    Download
                </Button>

                <Button
                    variant="danger"
                    onClick={onDelete}
                >
                    Delete
                </Button>
            </div>
        </div>
    );
};

export default DocumentCard;