'use client';

import React, { useState } from 'react';
import { Search, Download, Loader2 } from 'lucide-react';
import { api, SearchResult } from '@/lib/api';
import { useToast } from './Toast';

const BADGE_CLASS: Record<string, string> = {
    finance: 'badge-finance',
    legal: 'badge-legal',
    general: 'badge-general',
};

const TYPE_ICONS: Record<string, string> = {
    finance: '💰',
    legal: '⚖️',
    general: '📄',
};

function SimilarityBar({ score }: { score: number }) {
    const pct = Math.round(score * 100);
    const colorClass =
        pct >= 80 ? 'sim-excellent' : pct >= 60 ? 'sim-good' : 'sim-weak';
    return (
        <div className="sim-wrapper">
            <div className="sim-track">
                <div className={`sim-fill ${colorClass}`} style={{ width: `${pct}%` }} />
            </div>
            <span className={`sim-label ${colorClass}`}>{pct}% match</span>
        </div>
    );
}

function formatDate(iso: string) {
    try {
        return new Date(iso).toLocaleString();
    } catch {
        return iso;
    }
}

export default function SearchBar() {
    const { addToast } = useToast();
    const [query, setQuery] = useState('');
    const [topK, setTopK] = useState(5);
    const [results, setResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [searched, setSearched] = useState(false);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;
        setLoading(true);
        setSearched(true);
        try {
            const data = await api.searchDocuments(query.trim(), topK);
            setResults(data);
            if (data.length === 0) addToast('info', 'No results found. Try a different query.');
        } catch (err: unknown) {
            const msg = err instanceof Error ? err.message : 'Search failed.';
            addToast('error', msg);
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = async (bucket: string, fileName: string) => {
        try {
            const { download_url } = await api.getDownloadUrl(bucket, fileName);
            window.open(download_url, '_blank');
        } catch {
            addToast('error', 'Download failed. Please try again.');
        }
    };

    return (
        <div className="search-wrapper">
            <form className="search-form" onSubmit={handleSearch}>
                <div className="search-input-row">
                    <Search className="search-icon-prefix" size={20} />
                    <input
                        className="search-input"
                        type="text"
                        placeholder='Search documents... e.g. "tax information from Q4"'
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                    <button
                        className="btn btn-primary search-btn"
                        type="submit"
                        disabled={loading}
                    >
                        {loading ? <Loader2 size={18} className="spin" /> : <Search size={18} />}
                        {loading ? 'Searching...' : 'Search'}
                    </button>
                </div>
                <div className="search-topk-row">
                    <label className="topk-label">Results: <strong>{topK}</strong></label>
                    <input
                        type="range"
                        min={1}
                        max={10}
                        value={topK}
                        onChange={(e) => setTopK(Number(e.target.value))}
                        className="topk-slider"
                    />
                </div>
            </form>

            {searched && !loading && (
                <div className="results-section">
                    <p className="results-count">
                        {results.length > 0
                            ? `${results.length} result${results.length > 1 ? 's' : ''} found`
                            : 'No results found'}
                    </p>
                    <div className="results-grid">
                        {results.map((doc, idx) => (
                            <div key={idx} className="result-card glass-card">
                                <div className="result-card-header">
                                    <span className="result-file-icon">📄</span>
                                    <span className="result-filename">{doc.file_name}</span>
                                </div>
                                <div className="result-card-body">
                                    <span className={`badge ${BADGE_CLASS[doc.document_type] || 'badge-general'}`}>
                                        {TYPE_ICONS[doc.document_type]} {doc.document_type}
                                    </span>
                                    <SimilarityBar score={doc.similarity_score} />
                                    <p className="result-time">🕐 {formatDate(doc.upload_time)}</p>
                                </div>
                                <button
                                    className="btn btn-outline download-btn"
                                    onClick={() => handleDownload(doc.bucket_name, doc.file_name)}
                                >
                                    <Download size={16} />
                                    Download
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {!searched && (
                <div className="search-empty-state">
                    <p className="empty-hint">
                        💡 Try: <em>&quot;tax documents&quot;</em> · <em>&quot;contract terms&quot;</em> · <em>&quot;product roadmap&quot;</em>
                    </p>
                </div>
            )}
        </div>
    );
}
