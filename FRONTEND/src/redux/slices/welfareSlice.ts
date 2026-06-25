import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import React from 'react';

export interface Scheme {
  id: string;
  name: string;
  amount: string;
  eligibility: string[];
  provider?: string;
  deadline?: string;
  category?: string;
  description?: string;
}

export interface ChatMessage {
  sender: 'user' | 'bot';
  text: string;
  timestamp: string;
}

interface WelfareState {
  schemes: Scheme[];
  filters: {
    type: string[];
    amountRange: [number, number];
    eligibility: string[];
    deadline: string;
    provider: string[];
  };
  chatHistory: ChatMessage[];
  selectedScheme: Scheme | null;
}

const initialState: WelfareState = {
  schemes: [],
  filters: {
    type: [],
    amountRange: [0, 100000],
    eligibility: [],
    deadline: '',
    provider: [],
  },
  chatHistory: [],
  selectedScheme: null,
};

const welfareSlice = createSlice({
  name: 'welfare',
  initialState,
  reducers: {
    setSchemes(state, action: PayloadAction<Scheme[]>) {
      state.schemes = action.payload;
    },
    setFilters(state, action: PayloadAction<WelfareState['filters']>) {
      state.filters = action.payload;
    },
    setSelectedScheme(state, action: PayloadAction<Scheme | null>) {
      state.selectedScheme = action.payload;
    },
    addWelfareChatMessage(state, action: PayloadAction<ChatMessage>) {
      state.chatHistory.push(action.payload);
    },
    clearWelfareChat(state) {
      state.chatHistory = [];
    },
  },
});

export const { setSchemes, setFilters, setSelectedScheme, addWelfareChatMessage, clearWelfareChat } = welfareSlice.actions;
export default welfareSlice.reducer;
