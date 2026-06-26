import React, { useState, useRef } from 'react';
import styles from './digilocker.module.css';
import { Button } from '../Common/Button';
import { Badge } from '../Common/Badge';
import { Eye, Edit2, Trash2, Download, Upload, Check, X, FileText, ZoomIn, ZoomOut } from 'lucide-react';

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
    fileObject?: File; // actual file object if uploaded
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
    fileObject,
}) => {
    const [isEditing, setIsEditing] = useState(false);
    const [newName, setNewName] = useState(name);
    const [showViewer, setShowViewer] = useState(false);
    const [viewerZoom, setViewerZoom] = useState(100);
    const [objectUrl, setObjectUrl] = useState<string | null>(null);
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

    const getDocumentContent = () => {
        if (fileObject) return URL.createObjectURL(fileObject);
        if (url && url !== '#') return url;
        return null;
    };

    const handleView = () => {
        const docUrl = getDocumentContent();
        if (docUrl) {
            setObjectUrl(docUrl);
        } else {
            setObjectUrl(null);
        }
        setShowViewer(true);
        onView();
    };

    const handleCloseViewer = () => {
        setShowViewer(false);
        setViewerZoom(100);
    };

    const isViewable = ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'bmp'].includes(type.toLowerCase());
    const isImage = ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'bmp'].includes(type.toLowerCase());
    const isPdf = type.toLowerCase() === 'pdf';

    const handleLocalDownload = () => {
        const docUrl = getDocumentContent();

        if (docUrl && docUrl !== '#') {
            const a = document.createElement('a');
            a.href = docUrl;
            a.download = name.includes('.') ? name : `${name}.${type}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } else {
            // Generate a realistic dummy file based on type
            let blob: Blob;
            let filename: string;

            if (isPdf) {
                // Create a minimal valid PDF
                const pdfContent = `%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 120 >>
stream
BT
/F1 24 Tf
72 720 Td
(${name}) Tj
0 -40 Td
/F1 12 Tf
(Document Type: ${type.toUpperCase()}) Tj
0 -20 Td
(Uploaded: ${new Date(uploadDate).toLocaleDateString()}) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000068 00000 n
0000000125 00000 n
0000000274 00000 n
0000000447 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
528
%%EOF`;
                blob = new Blob([pdfContent], { type: 'application/pdf' });
                filename = name.endsWith('.pdf') ? name : `${name}.pdf`;
            } else if (type.toLowerCase() === 'doc' || type.toLowerCase() === 'docx') {
                blob = new Blob([
                    `Document: ${name}\n\nType: ${type.toUpperCase()}\nSize: ${formatSize(size)}\nUploaded: ${new Date(uploadDate).toLocaleDateString()}\n\nThis is a placeholder document content.\nIn a real implementation, the actual document content would appear here.`
                ], { type: 'application/msword' });
                filename = name.endsWith(`.${type}`) ? name : `${name}.${type}`;
            } else if (type.toLowerCase() === 'txt') {
                blob = new Blob([
                    `Document: ${name}\nType: ${type.toUpperCase()}\nSize: ${formatSize(size)}\nUploaded: ${new Date(uploadDate).toLocaleDateString()}`
                ], { type: 'text/plain' });
                filename = name.endsWith('.txt') ? name : `${name}.txt`;
            } else {
                blob = new Blob([
                    `Document: ${name}\nType: ${type.toUpperCase()}\nSize: ${formatSize(size)}\nUploaded: ${new Date(uploadDate).toLocaleDateString()}`
                ], { type: 'application/octet-stream' });
                filename = name.includes('.') ? name : `${name}.${type}`;
            }

            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(downloadUrl);
        }
        onDownload();
    };

    return (
        <>
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
                    <button className={styles.actionIconButton} onClick={handleView} title="View Document">
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

            {/* Document Viewer Modal */}
            {showViewer && (
                <div className={styles.viewerOverlay} onClick={handleCloseViewer}>
                    <div className={styles.viewerModal} onClick={(e) => e.stopPropagation()}>
                        {/* Viewer Header */}
                        <div className={styles.viewerHeader}>
                            <div className={styles.viewerHeaderLeft}>
                                <FileText size={18} style={{ color: '#ff9f0a' }} />
                                <span className={styles.viewerFileName}>{name}</span>
                                <span className={styles.viewerFileMeta}>{type.toUpperCase()} · {formatSize(size)}</span>
                            </div>
                            <div className={styles.viewerHeaderRight}>
                                {isViewable && (
                                    <>
                                        <button className={styles.viewerActionBtn} onClick={() => setViewerZoom(z => Math.max(50, z - 25))} title="Zoom Out">
                                            <ZoomOut size={16} />
                                        </button>
                                        <span className={styles.viewerZoomLabel}>{viewerZoom}%</span>
                                        <button className={styles.viewerActionBtn} onClick={() => setViewerZoom(z => Math.min(200, z + 25))} title="Zoom In">
                                            <ZoomIn size={16} />
                                        </button>
                                    </>
                                )}
                                <button className={styles.viewerActionBtn} onClick={handleLocalDownload} title="Download">
                                    <Download size={16} />
                                </button>
                                <button className={`${styles.viewerActionBtn} ${styles.viewerCloseBtn}`} onClick={handleCloseViewer} title="Close">
                                    <X size={16} />
                                </button>
                            </div>
                        </div>

                        {/* Viewer Body */}
                        <div className={styles.viewerBody}>
                            {objectUrl && isPdf ? (
                                <iframe
                                    src={objectUrl}
                                    className={styles.viewerIframe}
                                    style={{ transform: `scale(${viewerZoom / 100})`, transformOrigin: 'top center' }}
                                    title={name}
                                />
                            ) : objectUrl && isImage ? (
                                <div className={styles.viewerImageContainer}>
                                    <img
                                        src={objectUrl}
                                        alt={name}
                                        className={styles.viewerImage}
                                        style={{ transform: `scale(${viewerZoom / 100})` }}
                                    />
                                </div>
                            ) : (
                                <div className={styles.viewerPlaceholder}>
                                    <FileText size={64} style={{ color: 'rgba(255,255,255,0.15)', marginBottom: '1.5rem' }} />
                                    <h3 className={styles.viewerPlaceholderTitle}>{name}</h3>
                                    <p className={styles.viewerPlaceholderMeta}>
                                        {type.toUpperCase()} · {formatSize(size)} · Uploaded {new Date(uploadDate).toLocaleDateString()}
                                    </p>
                                    <p className={styles.viewerPlaceholderNote}>
                                        Preview not available for this file type.
                                    </p>
                                    <button className={styles.viewerDownloadCta} onClick={handleLocalDownload}>
                                        <Download size={16} />
                                        Download to View
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default DocumentCard;