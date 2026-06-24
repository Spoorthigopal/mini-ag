import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface ChatMessage {
  sender: 'user' | 'bot';
  text: string;
}

interface InterviewState {
  selectedJobId: string | null;
  started: boolean;
  chatMessages: ChatMessage[];
}

const initialState: InterviewState = {
  selectedJobId: null,
  started: false,
  chatMessages: [],
};

const interviewSlice = createSlice({
  name: 'interview',
  initialState,
  reducers: {
    setSelectedJob(state, action: PayloadAction<string>) {
      state.selectedJobId = action.payload;
    },
    startInterview(state) {
      state.started = true;
      state.chatMessages = [];
    },
    addChatMessage(state, action: PayloadAction<ChatMessage>) {
      state.chatMessages.push(action.payload);
    },
    clearChat(state) {
      state.chatMessages = [];
      state.started = false;
      state.selectedJobId = null;
    },
  },
});

export const { setSelectedJob, startInterview, addChatMessage, clearChat } = interviewSlice.actions;
export default interviewSlice.reducer;
