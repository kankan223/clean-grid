import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Type definitions
export interface User {
  id: string;
  email: string;
  role: 'citizen' | 'crew' | 'admin';
  points: number;
  createdAt: string;
  updatedAt: string;
}

export interface AuthState {
  // State
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
  updateProfile: (userData: Partial<User>) => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

// API functions
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8004';

interface LoginResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

interface RefreshResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

const apiLogin = async (email: string, password: string): Promise<LoginResponse> => {
  const response = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
      remember_me: false,
    }),
    credentials: 'include', // Important for cookies
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Login failed');
  }

  return response.json();
};

const apiRefreshToken = async (refreshToken: string): Promise<RefreshResponse> => {
  const response = await fetch(`${API_BASE}/api/auth/refresh`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      refresh_token: refreshToken,
    }),
    credentials: 'include', // Important for cookies
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Token refresh failed');
  }

  return response.json();
};

const apiLogout = async (): Promise<void> => {
  await fetch(`${API_BASE}/api/auth/logout`, {
    method: 'POST',
    credentials: 'include', // Important for cookies
  });
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await apiLogin(email, password);
          
          set({
            user: response.user,
            accessToken: response.accessToken,
            refreshToken: response.refreshToken,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          // Tokens are stored as HttpOnly cookies by the backend
          
        } catch (err) {
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            error: err instanceof Error ? err.message : 'Login failed',
          });
        }
      },

      logout: async () => {
        try {
          await apiLogout();
          
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          console.error('Logout error:', error);
        }
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get();
        
        if (!refreshToken) {
          get().logout();
          return;
        }
        
        try {
          const response = await apiRefreshToken(refreshToken);
          
          set({
            accessToken: response.accessToken,
            refreshToken: response.refreshToken,
            error: null,
          });
          // Tokens are updated as HttpOnly cookies by the backend
          
        } catch (error) {
          // Refresh failed, logout user
          get().logout();
        }
      },

      updateProfile: (userData: Partial<User>) => {
        const { user } = get();
        
        if (user) {
          const updatedUser: User = {
            ...user,
            ...userData,
            updatedAt: new Date().toISOString(),
          };
          
          set({ user: updatedUser });
        }
      },

      clearError: () => {
        set({ error: null });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },
    }),
    {
      name: 'cleangrid-auth',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Selectors for easy access
export const useAuth = () => useAuthStore((state) => state);
export const useUser = () => useAuthStore((state) => state.user);
export const useIsAuthenticated = () => useAuthStore((state) => state.isAuthenticated);
export const useIsAdmin = () => useAuthStore((state) => state.user?.role === 'admin');
export const useIsCrew = () => useAuthStore((state) => state.user?.role === 'crew');
export const useAuthLoading = () => useAuthStore((state) => state.isLoading);
export const useAuthError = () => useAuthStore((state) => state.error);

// Helper functions
export const hasRole = (user: User | null, role: User['role']): boolean => {
  return user?.role === role;
};

export const hasAnyRole = (user: User | null, roles: User['role'][]): boolean => {
  return user ? roles.includes(user.role) : false;
};

export const canAccessAdmin = (user: User | null): boolean => {
  return hasRole(user, 'admin');
};

export const canAccessCrew = (user: User | null): boolean => {
  return hasAnyRole(user, ['crew', 'admin']);
};
