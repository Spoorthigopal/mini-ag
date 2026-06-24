import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface Document {
  id: string;
  name: string;
  type: string; // e.g., 'pdf', 'doc', etc.
  category: 'Academic' | 'Professional' | 'Identity' | 'Financial';
  size: number; // bytes
  uploadedAt: string; // ISO date string
  url?: string; // optional download link
}

interface DocumentState {
  documents: Document[];
  uploading: boolean;
  uploadProgress: number; // 0-100
}

const initialState: DocumentState = {
  documents: [],
  uploading: false,
  uploadProgress: 0,
};

const documentSlice = createSlice({
  name: 'document',
  initialState,
  reducers: {
    addDocument(state, action: PayloadAction<Document>) {
      state.documents.push(action.payload);
    },
    deleteDocument(state, action: PayloadAction<string>) {
      state.documents = state.documents.filter((doc) => doc.id !== action.payload);
    },
    setUploading(state, action: PayloadAction<boolean>) {
      state.uploading = action.payload;
    },
    setUploadProgress(state, action: PayloadAction<number>) {
      state.uploadProgress = action.payload;
    },
    clearAll(state) {
      state.documents = [];
      state.uploading = false;
      state.uploadProgress = 0;
    },
  },
});

export const { addDocument, deleteDocument, setUploading, setUploadProgress, clearAll } =
  documentSlice.actions;
export default documentSlice.reducer;
