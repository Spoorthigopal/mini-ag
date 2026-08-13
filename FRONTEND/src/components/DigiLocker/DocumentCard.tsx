import React, { useState, useRef } from 'react';
import styles from './digilocker.module.css';
import { Eye, Trash2, Download, Shield, Edit2, Check, X, Upload, AlertCircle, CheckCircle, RefreshCw } from 'lucide-react';

interface DocumentCardProps {
  id: string;
  name: string;
  type: string;
  uploadDate: string;
  size: number;
  encrypted: boolean;
  isHighlighted: boolean;
  onDownload: () => void | Promise<void>;
  onDelete: () => void | Promise<void>;
  onView: () => void | Promise<void>;
  onRename: (newName: string) => Promise<boolean>;
  onReplace: (file: File) => Promise<boolean>;
}

const formatSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
};

const getFileIcon = (type: string): string => {
  const t = type.toLowerCase();
  if (t === 'pdf') return '📄';
  if (['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'].includes(t)) return '🖼️';
  if (['doc', 'docx'].includes(t)) return '📝';
  if (t === 'zip') return '🗜️';
  return '📁';
};

const DocumentCard: React.FC<DocumentCardProps> = ({
  id,
  name,
  type,
  uploadDate,
  size,
  encrypted,
  isHighlighted,
  onDownload,
  onDelete,
  onView,
  onRename,
  onReplace,
}) => {
  // Action states
  const [downloading, setDownloading] = useState(false);
  const [viewing, setViewing] = useState(false);

  // Edit panel
  const [editOpen, setEditOpen] = useState(false);

  // Rename sub-state
  const [renaming, setRenaming] = useState(false);
  const [renameValue, setRenameValue] = useState(name.replace(/\.[^.]+$/, '')); // name without extension
  const [renameLoading, setRenameLoading] = useState(false);
  const [renameMsg, setRenameMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Replace sub-state
  const [replaceFile, setReplaceFile] = useState<File | null>(null);
  const [replaceLoading, setReplaceLoading] = useState(false);
  const [replaceMsg, setReplaceMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDownload = async () => {
    setDownloading(true);
    try { await onDownload(); } finally { setDownloading(false); }
  };

  const handleView = async () => {
    setViewing(true);
    try { await onView(); } finally { setViewing(false); }
  };

  const handleToggleEdit = () => {
    setEditOpen((prev) => !prev);
    setRenaming(false);
    setRenameMsg(null);
    setReplaceFile(null);
    setReplaceMsg(null);
    setRenameValue(name.replace(/\.[^.]+$/, ''));
  };

  // --- Rename ---
  const handleRenameSubmit = async () => {
    const trimmed = renameValue.trim();
    if (!trimmed) {
      setRenameMsg({ type: 'error', text: 'Name cannot be empty.' });
      return;
    }
    setRenameLoading(true);
    setRenameMsg(null);
    const ok = await onRename(trimmed);
    setRenameLoading(false);
    if (ok) {
      setRenameMsg({ type: 'success', text: 'Renamed successfully!' });
      setTimeout(() => { setRenameMsg(null); setRenaming(false); }, 1500);
    } else {
      setRenameMsg({ type: 'error', text: 'Rename failed. Try again.' });
    }
  };

  // --- Replace ---
  const ALLOWED_EXT = ['pdf', 'png', 'jpg', 'jpeg', 'docx', 'zip'];

  const handleReplaceFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      const ext = f.name.split('.').pop()?.toLowerCase() || '';
      if (!ALLOWED_EXT.includes(ext)) {
        setReplaceMsg({ type: 'error', text: `Unsupported type: .${ext}. Allowed: PDF, PNG, JPG, DOCX, ZIP` });
        return;
      }
      if (f.size > 50 * 1024 * 1024) {
        setReplaceMsg({ type: 'error', text: 'File exceeds 50 MB limit.' });
        return;
      }
      setReplaceFile(f);
      setReplaceMsg(null);
    }
  };

  const handleReplaceSubmit = async () => {
    if (!replaceFile) return;
    setReplaceLoading(true);
    setReplaceMsg(null);
    const ok = await onReplace(replaceFile);
    setReplaceLoading(false);
    if (ok) {
      setReplaceMsg({ type: 'success', text: `Replaced & re-encrypted with "${replaceFile.name}"!` });
      setReplaceFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      setTimeout(() => { setReplaceMsg(null); setEditOpen(false); }, 2000);
    } else {
      setReplaceMsg({ type: 'error', text: 'Replace failed. Try again.' });
    }
  };

  const formattedDate = (() => {
    try {
      return new Date(uploadDate).toLocaleDateString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
      });
    } catch { return uploadDate; }
  })();

  const isViewable = ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'svg'].includes(type.toLowerCase());
  const origExt = name.includes('.') ? name.split('.').pop()! : type;

  return (
    <div className={`${styles.docCard} ${isHighlighted ? styles.docCardHighlighted : ''}`}>
      {/* Encrypted Badge */}
      {encrypted && (
        <div className={styles.encryptedBadge}>
          <Shield size={10} style={{ marginRight: '3px' }} />
          Encrypted
        </div>
      )}

      {/* File Icon & Info */}
      <div className={styles.docInfo}>
        <div style={{ fontSize: '2rem', lineHeight: 1, marginBottom: '0.5rem' }}>
          {getFileIcon(type)}
        </div>
        <h4 className={styles.docName} title={name}>{name}</h4>
        <p className={styles.docMeta}>
          <span className={styles.docMetaSpan}>{type.toUpperCase()}</span>
          <span className={styles.docMetaSpan}>•</span>
          <span className={styles.docMetaSpan}>{formatSize(size)}</span>
        </p>
        <p className={styles.docMeta} style={{ marginTop: '0.25rem' }}>
          Uploaded: {formattedDate}
        </p>
      </div>

      {/* Action Buttons */}
      <div className={styles.docActionsGrid}>
        {isViewable && (
          <button className={styles.actionIconButton} onClick={handleView}
            title="View in new tab" disabled={viewing} style={{ opacity: viewing ? 0.6 : 1 }}>
            <Eye size={18} />
          </button>
        )}

        <button className={`${styles.actionIconButton} ${styles.downloadBtn}`}
          onClick={handleDownload} title="Download (decrypted)"
          disabled={downloading} style={{ opacity: downloading ? 0.6 : 1 }}>
          <Download size={18} />
        </button>

        {/* Edit Button */}
        <button
          className={`${styles.actionIconButton} ${editOpen ? styles.editBtnActive : styles.editBtn}`}
          onClick={handleToggleEdit}
          title="Edit (rename / replace)"
        >
          <Edit2 size={18} />
        </button>

        <button className={`${styles.actionIconButton} ${styles.deleteBtn}`}
          onClick={onDelete} title="Delete Document">
          <Trash2 size={18} />
        </button>
      </div>

      {/* ──────── EDIT PANEL ──────── */}
      {editOpen && (
        <div className={styles.editPanel}>
          {/* ── Rename Section ── */}
          <div className={styles.editSection}>
            <div className={styles.editSectionHeader} onClick={() => { setRenaming((v) => !v); setRenameMsg(null); }}>
              <span className={styles.editSectionLabel}>✏️ Rename Document</span>
              <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: '0.75rem' }}>{renaming ? '▲' : '▼'}</span>
            </div>

            {renaming && (
              <div style={{ marginTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <input
                    className={styles.renameInput}
                    value={renameValue}
                    onChange={(e) => setRenameValue(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleRenameSubmit()}
                    placeholder="Enter new name (without extension)"
                    autoFocus
                    style={{ flex: 1 }}
                  />
                  <span style={{ color: 'rgba(255,255,255,0.35)', fontSize: '0.8rem', whiteSpace: 'nowrap' }}>
                    .{origExt}
                  </span>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    className={styles.editActionBtn}
                    onClick={handleRenameSubmit}
                    disabled={renameLoading}
                    style={{ background: 'rgba(48, 209, 88, 0.15)', color: '#30d158', flex: 1 }}
                  >
                    {renameLoading ? <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <Check size={14} />}
                    {renameLoading ? 'Saving…' : 'Save Name'}
                  </button>
                  <button
                    className={styles.editActionBtn}
                    onClick={() => { setRenaming(false); setRenameMsg(null); setRenameValue(name.replace(/\.[^.]+$/, '')); }}
                    style={{ background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.5)' }}
                  >
                    <X size={14} /> Cancel
                  </button>
                </div>

                {renameMsg && (
                  <div className={renameMsg.type === 'success' ? styles.msgSuccess : styles.msgError}>
                    {renameMsg.type === 'success' ? <CheckCircle size={13} /> : <AlertCircle size={13} />}
                    {renameMsg.text}
                  </div>
                )}
              </div>
            )}

            {!renaming && (
              <button className={styles.editTriggerBtn} onClick={() => setRenaming(true)}>
                <Edit2 size={13} /> Click to rename
              </button>
            )}
          </div>

          {/* ── Replace Section ── */}
          <div className={styles.editSection} style={{ borderTop: '1px solid rgba(255,255,255,0.07)', paddingTop: '0.875rem' }}>
            <div className={styles.editSectionHeader}>
              <span className={styles.editSectionLabel}>🔄 Replace with New File</span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.35)', margin: '0.25rem 0 0.625rem' }}>
              File is re-encrypted automatically. Category &amp; ID stay the same.
            </p>

            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.docx,.zip"
              style={{ display: 'none' }}
              onChange={handleReplaceFileChange}
            />

            {replaceFile ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <div style={{
                  background: 'rgba(255,159,10,0.1)',
                  border: '1px solid rgba(255,159,10,0.25)',
                  borderRadius: '0.5rem',
                  padding: '0.5rem 0.75rem',
                  fontSize: '0.8rem',
                  color: '#ff9f0a',
                  display: 'flex', alignItems: 'center', gap: '0.5rem',
                }}>
                  📎 {replaceFile.name} ({formatSize(replaceFile.size)})
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    className={styles.editActionBtn}
                    onClick={handleReplaceSubmit}
                    disabled={replaceLoading}
                    style={{ background: 'rgba(255,159,10,0.15)', color: '#ff9f0a', flex: 1 }}
                  >
                    {replaceLoading
                      ? <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} />
                      : <Upload size={14} />}
                    {replaceLoading ? 'Encrypting…' : 'Confirm Replace'}
                  </button>
                  <button
                    className={styles.editActionBtn}
                    onClick={() => { setReplaceFile(null); if (fileInputRef.current) fileInputRef.current.value = ''; setReplaceMsg(null); }}
                    style={{ background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.5)' }}
                  >
                    <X size={14} /> Cancel
                  </button>
                </div>
              </div>
            ) : (
              <button
                className={styles.editTriggerBtn}
                onClick={() => fileInputRef.current?.click()}
                style={{ borderColor: 'rgba(255,159,10,0.25)', color: '#ff9f0a' }}
              >
                <Upload size={13} /> Select new file to replace
              </button>
            )}

            {replaceMsg && (
              <div className={replaceMsg.type === 'success' ? styles.msgSuccess : styles.msgError} style={{ marginTop: '0.5rem' }}>
                {replaceMsg.type === 'success' ? <CheckCircle size={13} /> : <AlertCircle size={13} />}
                {replaceMsg.text}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentCard;