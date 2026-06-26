import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// Matches the backend DocumentResponse schema exactly
export interface Document {
  document_id: string;        // UUID from backend
  document_name: string;      // filename shown to user
  category: string;           // e.g. 'certificates', 'transcripts', etc.
  file_size: number;          // bytes (original, pre-encryption)
  upload_date: string;        // ISO datetime string
  last_accessed: string;      // ISO datetime string
  encrypted: boolean;         // always true – stored encrypted in DB
  checksum: string;           // SHA-256 of original file
}

interface DocumentState {
  documents: Document[];
  selectedCategory: string;
  uploadProgress: number;     // 0-100
  uploading: boolean;
  loading: boolean;
  error: string | null;
}

const initialState: DocumentState = {
  documents: [],
  selectedCategory: 'All',
  uploadProgress: 0,
  uploading: false,
  loading: false,
  error: null,
};

const documentSlice = createSlice({
  name: 'document',
  initialState,
  reducers: {
    setDocuments(state, action: PayloadAction<Document[]>) {
      state.documents = action.payload;
    },
    addDocument(state, action: PayloadAction<Document>) {
      state.documents.unshift(action.payload); // newest first
    },
    deleteDocument(state, action: PayloadAction<string>) {
      state.documents = state.documents.filter(
        (doc) => doc.document_id !== action.payload
      );
    },
    updateDocument(state, action: PayloadAction<Document>) {
      const index = state.documents.findIndex(
        (doc) => doc.document_id === action.payload.document_id
      );
      if (index !== -1) {
        state.documents[index] = action.payload;
      }
    },
    setSelectedCategory(state, action: PayloadAction<string>) {
      state.selectedCategory = action.payload;
    },
    setUploadProgress(state, action: PayloadAction<number>) {
      state.uploadProgress = action.payload;
    },
    setUploading(state, action: PayloadAction<boolean>) {
      state.uploading = action.payload;
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.loading = action.payload;
    },
    setError(state, action: PayloadAction<string | null>) {
      state.error = action.payload;
    },
    clearAll(state) {
      state.documents = [];
      state.selectedCategory = 'All';
      state.uploadProgress = 0;
      state.uploading = false;
      state.loading = false;
      state.error = null;
    },
  },
});

export const {
  setDocuments,
  addDocument,
  deleteDocument,
  updateDocument,
  setSelectedCategory,
  setUploadProgress,
  setUploading,
  setLoading,
  setError,
  clearAll,
} = documentSlice.actions;

export default documentSlice.reducer;
