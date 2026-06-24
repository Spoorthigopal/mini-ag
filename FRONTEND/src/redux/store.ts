// Redux Store Configuration
// Generated from Prompt 3

import { configureStore } from '@reduxjs/toolkit'

// Slices will be imported here

export const store = configureStore({
  reducer: {
    // Slices configured here
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

export default store
