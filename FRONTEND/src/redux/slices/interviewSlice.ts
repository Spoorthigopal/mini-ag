import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface ChatMessage {
  sender: 'user' | 'bot';
  text: string;
  timestamp: string;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  description: string;
}

interface InterviewState {
  sessionId: string | null;
  messages: ChatMessage[];
  currentJob: Job | null;
  feedback: {
    score: number;
    strengths: string[];
    improvements: string[];
    summary: string;
  } | null;
  isActive: boolean;
}

const initialState: InterviewState = {
  sessionId: null,
  messages: [],
  currentJob: null,
  feedback: null,
  isActive: false,
};

const interviewSlice = createSlice({
  name: 'interview',
  initialState,
  reducers: {
    startSession(state, action: PayloadAction<{ sessionId: string; job: Job }>) {
      state.sessionId = action.payload.sessionId;
      state.currentJob = action.payload.job;
      state.messages = [];
      state.feedback = null;
      state.isActive = true;
    },
    addMessage(state, action: PayloadAction<ChatMessage>) {
      state.messages.push(action.payload);
    },
    setFeedback(state, action: PayloadAction<InterviewState['feedback']>) {
      state.feedback = action.payload;
    },
    endSession(state) {
      state.isActive = false;
    },
    clearInterview(state) {
      state.sessionId = null;
      state.messages = [];
      state.currentJob = null;
      state.feedback = null;
      state.isActive = false;
    },
  },
});

export const { startSession, addMessage, setFeedback, endSession, clearInterview } = interviewSlice.actions;
export default interviewSlice.reducer;
