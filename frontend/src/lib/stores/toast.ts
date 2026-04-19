'use client';

import { create } from 'zustand';

export type ToastVariant = 'info' | 'success' | 'error';

export interface ToastMessage {
  id: string;
  title: string;
  description?: string;
  variant: ToastVariant;
}

interface ToastStore {
  messages: ToastMessage[];
  push: (message: Omit<ToastMessage, 'id'>) => void;
  dismiss: (id: string) => void;
}

export const useToastStore = create<ToastStore>((set) => ({
  messages: [],
  push: (message) => {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    const next = { id, ...message };

    set((state) => ({ messages: [...state.messages, next] }));

    setTimeout(() => {
      set((state) => ({
        messages: state.messages.filter((item) => item.id !== id),
      }));
    }, 4500);
  },
  dismiss: (id) => {
    set((state) => ({
      messages: state.messages.filter((item) => item.id !== id),
    }));
  },
}));