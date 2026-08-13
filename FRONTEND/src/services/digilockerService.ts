import api from './api';
import { getToken } from './authService';

export interface DigiLockerDocument {
  document_id: string;
  document_name: string;
  category: string;
  file_size: number;
  upload_date: string;
  last_accessed: string;
  encrypted: boolean;
  checksum: string;
}

export interface DocumentListResponse {
  total_documents: number;
  category_filter: string | null;
  documents: DigiLockerDocument[];
  storage_used: number;
  storage_limit: number;
}

/**
 * Upload a document to the DigiLocker.
 * The backend encrypts it with AES-256-GCM keyed from the user's ID.
 */
export const uploadDocument = async (
  file: File,
  category: string,
  documentName?: string,
  description?: string
): Promise<DigiLockerDocument> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('category', category);
  if (documentName) formData.append('document_name', documentName);
  if (description) formData.append('description', description);

  const response = await api.post('/digilocker/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

/**
 * Fetch all documents for the authenticated user.
 */
export const listDocuments = async (
  category?: string,
  page = 1,
  limit = 50
): Promise<DocumentListResponse> => {
  const params: Record<string, any> = { page, limit };
  if (category) params.category = category;

  const response = await api.get('/digilocker/documents', { params });
  return response.data;
};

/**
 * Download a document: decrypted file bytes are returned as a Blob.
 * Triggers a browser download.
 */
export const downloadDocument = async (
  docId: string,
  filename: string
): Promise<void> => {
  const response = await api.get(`/digilocker/download/${docId}`, {
    responseType: 'blob',
  });

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};

/**
 * View a document in a new browser tab.
 * Decrypts the file on the backend and streams it inline.
 * Falls back to the download endpoint with an object URL opened in a new tab.
 */
export const viewDocument = async (
  docId: string,
  filename: string
): Promise<void> => {
  // Use the view endpoint (inline content-disposition)
  const token = getToken();
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
  const viewUrl = `${baseURL}/digilocker/view/${docId}?token=${token}`;
  window.open(viewUrl, '_blank');
};

/**
 * Delete a document.
 */
export const deleteDocument = async (docId: string): Promise<void> => {
  await api.delete(`/digilocker/${docId}`);
};

/**
 * Rename a document (metadata-only update, encrypted data is untouched).
 */
export const renameDocument = async (
  docId: string,
  newName: string
): Promise<DigiLockerDocument> => {
  const formData = new FormData();
  formData.append('new_name', newName);
  const response = await api.patch(`/digilocker/${docId}/rename`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

/**
 * Replace a document's encrypted content with a new file.
 * The backend re-encrypts the new file and updates all encryption fields in-place.
 */
export const replaceDocument = async (
  docId: string,
  file: File
): Promise<DigiLockerDocument> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.put(`/digilocker/${docId}/replace`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

