import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  type: string; // e.g., 'Full-time', 'Part-time', 'Remote'
  description: string;
  requirements: string[];
  salary?: string;
  deadline?: string;
}

export interface ChatMessage {
  sender: 'user' | 'bot';
  text: string;
  timestamp: string;
}

export interface ResumeData {
  fileName: string | null;
  parsedData: any | null;
  parsedAt: string | null;
}

interface InternshipState {
  jobs: Job[];
  filters: {
    role: string[];
    location: string[];
    type: string[];
  };
  resumeData: ResumeData;
  chatHistory: ChatMessage[];
  selectedJob: Job | null;
}

const initialState: InternshipState = {
  jobs: [],
  filters: {
    role: [],
    location: [],
    type: [],
  },
  resumeData: {
    fileName: null,
    parsedData: null,
    parsedAt: null,
  },
  chatHistory: [],
  selectedJob: null,
};

const internshipSlice = createSlice({
  name: 'internship',
  initialState,
  reducers: {
    setJobs(state, action: PayloadAction<Job[]>) {
      state.jobs = action.payload;
    },
    setFilters(state, action: PayloadAction<InternshipState['filters']>) {
      state.filters = action.payload;
    },
    setResumeData(state, action: PayloadAction<ResumeData>) {
      state.resumeData = action.payload;
    },
    setSelectedJob(state, action: PayloadAction<Job | null>) {
      state.selectedJob = action.payload;
    },
    addInternshipChatMessage(state, action: PayloadAction<ChatMessage>) {
      state.chatHistory.push(action.payload);
    },
    clearInternshipChat(state) {
      state.chatHistory = [];
    },
  },
});

export const {
  setJobs,
  setFilters,
  setResumeData,
  setSelectedJob,
  addInternshipChatMessage,
  clearInternshipChat,
} = internshipSlice.actions;
export default internshipSlice.reducer;
