'use client';

import { useState } from 'react';
import UploadZone from '@/components/UploadZone';
import SearchBar from '@/components/SearchBar';
import DocumentList from '@/components/DocumentList';
import { useAuth } from '@/context/AuthContext';
import { LogOut } from 'lucide-react';

type Tab = 'upload' | 'search' | 'documents';

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: 'upload', label: 'Upload', icon: '📤' },
  { id: 'search', label: 'Search', icon: '🔍' },
  { id: 'documents', label: 'Documents', icon: '📁' },
];

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>('upload');
  const [docRefreshKey, setDocRefreshKey] = useState(0);
  const { user, logout } = useAuth();

  const handleUploadSuccess = () => {
    setDocRefreshKey((k) => k + 1);
  };

  return (
    <div className="app-shell">
      {/* ── Header ── */}
      <header className="header">
        <div className="header-brand">
          <div className="header-logo">🧠</div>
          <div>
            <h1 className="header-title">Synapse Storage</h1>
            <p className="header-subtitle">Semantic Document Gateway</p>
          </div>
        </div>

        {user && (
          <div className="user-profile">
            <span className="user-email">{user.email}</span>
            <button onClick={logout} className="action-btn delete" style={{ display: 'flex', alignItems: 'center', gap: '4px', background: 'transparent', border: 'none' }} title="Logout">
              <LogOut size={16} /> Logout
            </button>
          </div>
        )}
      </header>

      {/* ── Tab Nav ── */}
      <nav className="tab-nav" role="tablist">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </nav>

      {/* ── Content ── */}
      <main>
        {activeTab === 'upload' && (
          <section className="fade-up">
            <h2 className="section-title">📤 Upload Document</h2>
            <UploadZone onUploadSuccess={handleUploadSuccess} />
          </section>
        )}

        {activeTab === 'search' && (
          <section className="fade-up">
            <h2 className="section-title">🔍 Semantic Search</h2>
            <SearchBar />
          </section>
        )}

        {activeTab === 'documents' && (
          <section className="fade-up">
            <h2 className="section-title">📁 All Documents</h2>
            <DocumentList refreshKey={docRefreshKey} />
          </section>
        )}
      </main>
    </div>
  );
}
