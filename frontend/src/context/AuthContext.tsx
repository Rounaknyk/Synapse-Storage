'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { useRouter, usePathname } from 'next/navigation';
import { useToast } from '@/components/Toast';

interface AuthContextType {
    user: User | null;
    loading: boolean;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    loading: true,
    logout: async () => { },
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();
    const pathname = usePathname();
    const { addToast } = useToast();

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
            setUser(currentUser);
            setLoading(false);

            // Redirect logic
            if (!currentUser && pathname !== '/login' && pathname !== '/signup') {
                router.push('/login');
            } else if (currentUser && (pathname === '/login' || pathname === '/signup')) {
                router.push('/');
            }
        });

        return () => unsubscribe();
    }, [pathname, router]);

    const logout = async () => {
        try {
            await signOut(auth);
            router.push('/login');
            addToast('success', 'Logged out successfully');
        } catch (error) {
            console.error('Logout error:', error);
            addToast('error', 'Failed to log out');
        }
    };

    return (
        <AuthContext.Provider value={{ user, loading, logout }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
