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
  selectedCategory: 'Academic' | 'Professional' | 'Identity' | 'Financial' | 'All';
  uploadProgress: number; // 0-100
  uploading?: boolean;
}

const initialState: DocumentState = {
  documents: [],
  selectedCategory: 'All',
  uploadProgress: 0,
  uploading: false,
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
    updateDocument(state, action: PayloadAction<Document>) {
      const index = state.documents.findIndex(doc => doc.id === action.payload.id);
      if (index !== -1) {
        state.documents[index] = action.payload;
      }
    },
    setSelectedCategory(state, action: PayloadAction<DocumentState['selectedCategory']>) {
      state.selectedCategory = action.payload;
    },
    setUploadProgress(state, action: PayloadAction<number>) {
      state.uploadProgress = action.payload;
    },
    setUploading(state, action: PayloadAction<boolean>) {
      state.uploading = action.payload;
    },
    clearAll(state) {
      state.documents = [];
      state.selectedCategory = 'All';
      state.uploadProgress = 0;
      state.uploading = false;
    },
  },
});

export const { addDocument, deleteDocument, updateDocument, setSelectedCategory, setUploadProgress, setUploading, clearAll } =
  documentSlice.actions;
export default documentSlice.reducer;
