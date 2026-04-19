'use client';

import { X } from 'lucide-react';

import { useToastStore } from '@/lib/stores/toast';

const variantClasses = {
  info: 'border-slate-300 bg-white text-slate-900',
  success: 'border-emerald-200 bg-emerald-50 text-emerald-900',
  error: 'border-rose-200 bg-rose-50 text-rose-900',
};

export function useToast() {
  const push = useToastStore((state) => state.push);
  return { toast: push };
}

export function ToastViewport() {
  const messages = useToastStore((state) => state.messages);
  const dismiss = useToastStore((state) => state.dismiss);

  return (
    <div className="pointer-events-none fixed right-4 top-4 z-[100] flex w-full max-w-sm flex-col gap-2">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`pointer-events-auto rounded-md border p-3 shadow-sm ${variantClasses[message.variant]}`}
          role="status"
          aria-live="polite"
        >
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="text-sm font-semibold">{message.title}</p>
              {message.description ? (
                <p className="mt-1 text-sm opacity-90">{message.description}</p>
              ) : null}
            </div>
            <button
              type="button"
              onClick={() => dismiss(message.id)}
              className="rounded p-1 opacity-70 transition hover:opacity-100"
              aria-label="Dismiss notification"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}