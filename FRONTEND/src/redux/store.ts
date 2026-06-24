import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import welfareReducer from './slices/welfareSlice';
import internshipReducer from './slices/internshipSlice';
import interviewReducer from './slices/interviewSlice';
import documentReducer from './slices/documentSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    welfare: welfareReducer,
    internship: internshipReducer,
    interview: interviewReducer,
    document: documentReducer,
  },
});

type RootState = ReturnType<typeof store.getState>;
export type { RootState };
export type AppDispatch = typeof store.dispatch;
