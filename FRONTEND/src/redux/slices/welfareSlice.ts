import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import React from 'react';

export interface Scheme {
  id: string;
  name: string;
  amount: string;
  eligibility: string[];
  provider?: string;
  deadline?: string;
  icon?: React.ReactNode;
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
  },
});

export const { setSchemes, setFilters } = welfareSlice.actions;
export default welfareSlice.reducer;
