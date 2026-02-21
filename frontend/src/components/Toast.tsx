'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';

interface Toast {
    id: number;
    type: 'success' | 'error' | 'info';
    message: string;
}

const ToastContext = createContext<{
    addToast: (type: Toast['type'], message: string) => void;
} | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
    const [toasts, setToasts] = useState<Toast[]>([]);
    let counter = 0;

    const addToast = useCallback((type: Toast['type'], message: string) => {
        const id = ++counter;
        setToasts((prev) => [...prev, { id, type, message }]);
        setTimeout(() => {
            setToasts((prev) => prev.filter((t) => t.id !== id));
        }, 4000);
    }, []);

    return (
        <ToastContext.Provider value={{ addToast }}>
            {children}
            <div className="toast-container">
                {toasts.map((toast) => (
                    <div key={toast.id} className={`toast toast-${toast.type}`}>
                        <span className="toast-icon">
                            {toast.type === 'success' ? '✅' : toast.type === 'error' ? '❌' : 'ℹ️'}
                        </span>
                        <span>{toast.message}</span>
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
}

export function useToast() {
    const ctx = useContext(ToastContext);
    if (!ctx) throw new Error('useToast must be inside ToastProvider');
    return ctx;
}
