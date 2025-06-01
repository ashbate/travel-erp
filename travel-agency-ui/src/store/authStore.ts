import create from 'zustand';
import { persist } from 'zustand/middleware';
import apiClient from '../services/apiService'; // Assuming apiClient is default export
import { User } from '../types'; // Assuming User type is in types/index.ts or types/authTypes.ts

interface AuthState {
  token: string | null;
  user: User | null;
  setToken: (token: string) => void;
  fetchUser: () => Promise<void>; // New function to fetch user
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      setToken: (token) => {
        set({ token });
        localStorage.setItem('authToken', token);
        // After setting token, fetch user details
        if (token) {
          get().fetchUser();
        }
      },
      fetchUser: async () => {
        try {
          const response = await apiClient.get<User>('/users/me'); // apiClient from apiService.ts
          set({ user: response.data });
        } catch (error) {
          console.error("Failed to fetch user", error);
          // Optionally clear auth if user fetch fails critically
          // get().clearAuth();
        }
      },
      clearAuth: () => {
        set({ token: null, user: null });
        localStorage.removeItem('authToken');
      },
    }),
    {
      name: 'auth-storage',
      onRehydrateStorage: () => (state) => {
        const tokenFromStorage = localStorage.getItem('authToken');
        if (tokenFromStorage && !state?.token) {
            state?.setToken(tokenFromStorage); // This will also trigger fetchUser due to setToken logic
        } else if (tokenFromStorage && state?.token && !state.user) {
            // If token exists but user is not hydrated (e.g. direct call to setToken from localStorage without full rehydrate logic)
            state?.fetchUser();
        }
      }
    }
  )
);

// Initial fetch if token exists but user is not in store (e.g. after refresh and basic rehydration)
// The onRehydrateStorage should ideally handle this, but this is a fallback.
// Need to be careful not to call setToken if it's already being set by rehydration to avoid loops.
const currentState = useAuthStore.getState();
const tokenFromStorage = localStorage.getItem('authToken');

if (tokenFromStorage && tokenFromStorage !== currentState.token) {
    // If localStorage has a token and it's different from the initial store token (likely null)
    currentState.setToken(tokenFromStorage);
} else if (tokenFromStorage && currentState.token && !currentState.user) {
    // If token is in store (possibly from rehydration) but user is missing
    currentState.fetchUser();
}
