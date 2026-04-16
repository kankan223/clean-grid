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

// Mock API functions - these will be replaced with actual API calls
const mockLogin = async (email: string, _password: string): Promise<{
  user: User;
  accessToken: string;
  refreshToken: string;
}> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock user data
  const mockUser: User = {
    id: 'user-123',
    email,
    role: email.includes('admin') ? 'admin' : email.includes('crew') ? 'crew' : 'citizen',
    points: 0,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  return {
    user: mockUser,
    accessToken: `mock-access-token-${Date.now()}`,
    refreshToken: `mock-refresh-token-${Date.now()}`,
  };
};

const mockRefreshToken = async (_refreshToken: string): Promise<{
  accessToken: string;
  refreshToken: string;
}> => {
  await new Promise(resolve => setTimeout(resolve, 500));
  
  return {
    accessToken: `mock-access-token-${Date.now()}`,
    refreshToken: `mock-refresh-token-${Date.now()}`,
  };
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
          const response = await mockLogin(email, password);
          
          set({
            user: response.user,
            accessToken: response.accessToken,
            refreshToken: response.refreshToken,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });

          // Store tokens in HttpOnly cookies (handled by API)
          // For now, we'll store them in memory and persist middleware
          document.cookie = `access_token=${response.accessToken}; path=/; max-age=900; secure; samesite=strict`;
          document.cookie = `refresh_token=${response.refreshToken}; path=/; max-age=604800; secure; samesite=strict`;
          
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

      logout: () => {
        // Clear cookies
        document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        document.cookie = 'refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get();
        
        if (!refreshToken) {
          get().logout();
          return;
        }

        try {
          const response = await mockRefreshToken(refreshToken);
          
          set({
            accessToken: response.accessToken,
            refreshToken: response.refreshToken,
            error: null,
          });

          // Update cookies
          document.cookie = `access_token=${response.accessToken}; path=/; max-age=900; secure; samesite=strict`;
          document.cookie = `refresh_token=${response.refreshToken}; path=/; max-age=604800; secure; samesite=strict`;
          
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
