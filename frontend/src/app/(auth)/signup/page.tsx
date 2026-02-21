'use client';

import { useState } from 'react';
import { auth } from '@/lib/firebase';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { useRouter } from 'next/navigation';
import { useToast } from '@/components/Toast';
import Link from 'next/link';

export default function SignupPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const router = useRouter();
    const { addToast } = useToast();

    const handleSignup = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await createUserWithEmailAndPassword(auth, email, password);
            addToast('success', 'Account created successfully!');
            router.push('/');
        } catch (error: any) {
            console.error('Signup error:', error);
            addToast('error', error.message || 'Failed to create account.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card glass-card">
                <div className="auth-header">
                    <h2>Initialize Node</h2>
                    <p>Create a secure account to start archiving knowledge.</p>
                </div>

                <form onSubmit={handleSignup} className="auth-form">
                    <div className="form-group">
                        <label>Email Address</label>
                        <input
                            type="email"
                            className="input-field"
                            placeholder="agent@synapse.ai"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            className="input-field"
                            placeholder="At least 6 characters"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            minLength={6}
                        />
                    </div>

                    <button type="submit" className="btn btn-primary w-full mt-4" disabled={loading}>
                        {loading ? 'Initializing...' : 'Create Account'}
                    </button>
                </form>

                <div className="auth-footer">
                    <p>Already have access? <Link href="/login" className="auth-link">Sign In</Link></p>
                </div>
            </div>
        </div>
    );
}
