'use client';

import React, { useState } from 'react';
import { Search, Download, Loader2, Sparkles, BookOpen } from 'lucide-react';
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
    // Updated thresholds: 70%+ Excellent, 40-69% Good, below 40% Weak
    const colorClass = pct >= 70 ? 'sim-excellent' : pct >= 40 ? 'sim-good' : 'sim-weak';
    const colorLabel = pct >= 70 ? 'Excellent' : pct >= 40 ? 'Good' : 'Weak';
    return (
        <div className="sim-wrapper">
            <div className="sim-info">
                <span className="sim-percentage">{pct}%</span>
                <span className={`sim-quality ${colorClass}`}>{colorLabel}</span>
            </div>
            <div className="sim-track">
                <div className={`sim-fill ${colorClass}`} style={{ width: `${pct}%` }} />
            </div>
        </div>
    );
}

function formatDate(iso: string) {
    try { return new Date(iso).toLocaleString(); } catch { return iso; }
}

type SearchPhase = 'idle' | 'searching' | 'generating' | 'done';

export default function SearchBar() {
    const { addToast } = useToast();
    const [query, setQuery] = useState('');
    const [topK, setTopK] = useState(5);
    const [minSimilarity, setMinSimilarity] = useState(0.35); // Lowered from 0.6 to 0.35 for better semantic search
    const [ragAnswer, setRagAnswer] = useState<string | null>(null);
    const [sources, setSources] = useState<SearchResult[]>([]);
    const [phase, setPhase] = useState<SearchPhase>('idle');
    const [searched, setSearched] = useState(false);

    const loading = phase === 'searching' || phase === 'generating';

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        const trimmed = query.trim();
        if (!trimmed) return;

        setSearched(true);
        setRagAnswer(null);
        setSources([]);
        setPhase('searching');

        try {
            // Single backend call: full RAG pipeline (retrieve → augment → generate)
            const response = await api.smartSearch(trimmed, topK, minSimilarity);

            setPhase('generating');
            await new Promise((r) => setTimeout(r, 400)); // brief UX pause while "generating" shows

            setRagAnswer(response.rag_answer);
            setSources(response.sources);

            if (response.sources.length === 0)
                addToast('info', 'No matching documents found. Try a broader query.');
        } catch (err: unknown) {
            const msg = err instanceof Error ? err.message : 'Search failed.';
            addToast('error', msg);
        } finally {
            setPhase('done');
        }
    };

    const handleDownload = async (bucket: string, fileName: string) => {
        try {
            const { download_url } = await api.getDownloadUrl(bucket, fileName, false);
            const a = document.createElement('a');
            a.href = download_url;
            a.download = fileName; // Optional, might be governed by header
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } catch {
            addToast('error', 'Download failed. Please try again.');
        }
    };

    const handleViewDocument = async (bucket: string, fileName: string) => {
        try {
            const { download_url } = await api.getDownloadUrl(bucket, fileName, true);
            window.open(download_url, '_blank');
        } catch {
            addToast('error', 'Unable to open document. Please try again.');
        }
    };

    return (
        <div className="search-wrapper">

            {/* ── Search Form ── */}
            <form className="search-form" onSubmit={handleSearch}>
                <div className="search-input-row">
                    <Search className="search-icon-prefix" size={20} />
                    <input
                        className="search-input"
                        type="text"
                        placeholder='Ask anything — "what was our Q3 revenue?" or "find contract termination terms"'
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                    <button className="btn btn-primary search-btn" type="submit" disabled={loading}>
                        {phase === 'searching' ? (
                            <><Loader2 size={18} className="spin" /> Retrieving…</>
                        ) : phase === 'generating' ? (
                            <><Sparkles size={18} className="spin" /> Generating…</>
                        ) : (
                            <><Sparkles size={18} /> Ask AI</>
                        )}
                    </button>
                </div>

                <div className="search-topk-row">
                    <label className="topk-label">Top docs: <strong>{topK}</strong></label>
                    <input type="range" min={1} max={10} value={topK}
                        onChange={(e) => setTopK(Number(e.target.value))} className="topk-slider" />
                </div>
                <div className="search-topk-row">
                    <label className="topk-label">Min similarity: <strong>{Math.round(minSimilarity * 100)}%</strong></label>
                    <input type="range" min={0} max={100} step={5}
                        value={minSimilarity * 100}
                        onChange={(e) => setMinSimilarity(Number(e.target.value) / 100)}
                        className="topk-slider" />
                </div>
            </form>

            {/* ── Phase indicators ── */}
            {phase === 'searching' && (
                <div className="search-phase-indicator fade-up">
                    <Loader2 size={16} className="spin phase-icon-search" />
                    <span>Retrieving relevant documents via vector search…</span>
                </div>
            )}
            {phase === 'generating' && (
                <div className="search-phase-indicator fade-up">
                    <Sparkles size={16} className="spin phase-icon-ai" />
                    <span>Gemini is reading the documents and generating your answer…</span>
                </div>
            )}

            {/* ── RAG Answer Card ── */}
            {searched && phase === 'done' && ragAnswer && (
                <div className="rag-answer-card fade-up">
                    <div className="rag-answer-header">
                        <Sparkles size={18} className="rag-icon" />
                        <span className="rag-answer-label">AI Answer</span>
                        <span className="rag-answer-badge">Based on {sources.length} document{sources.length !== 1 ? 's' : ''}</span>
                    </div>
                    <p className="rag-answer-text">{ragAnswer}</p>
                    <div className="rag-answer-footer">
                        <BookOpen size={13} />
                        <span>Answer grounded in your documents · Powered by Gemini</span>
                    </div>
                </div>
            )}

            {/* ── Source Documents ── */}
            {searched && phase === 'done' && sources.length > 0 && (
                <div className="results-section">
                    <div className="results-header">
                        <p className="results-count">
                            📚 {sources.length} source document{sources.length > 1 ? 's' : ''} used
                        </p>
                        <div className="similarity-legend">
                            <span className="legend-title">Match Quality:</span>
                            <span className="legend-item"><span className="legend-dot sim-excellent" />80-100% Excellent</span>
                            <span className="legend-item"><span className="legend-dot sim-good" />60-79% Good</span>
                            <span className="legend-item"><span className="legend-dot sim-weak" />&lt;60% Weak</span>
                        </div>
                    </div>
                    <div className="results-grid">
                        {sources.map((doc, idx) => (
                            <div key={idx} className="result-card glass-card clickable-card" onClick={() => handleViewDocument(doc.bucket_name, doc.file_name)}>
                                <div className="result-card-header">
                                    <span className="result-file-icon">📄</span>
                                    <span className="result-filename">{doc.file_name}</span>
                                </div>
                                <div className="result-card-body">
                                    <span className={`badge ${BADGE_CLASS[doc.document_type] || 'badge-general'}`}>
                                        {TYPE_ICONS[doc.document_type]} {doc.document_type}
                                    </span>
                                    <SimilarityBar score={doc.similarity_score} />
                                    {doc.preview && (
                                        <div className="result-preview">
                                            <span className="result-preview-label">📝 Matched snippet</span>
                                            <p className="result-preview-text">{doc.preview}</p>
                                        </div>
                                    )}
                                    <p className="result-time">🕐 {formatDate(doc.upload_time)}</p>
                                </div>
                                <button
                                    className="btn btn-outline download-btn"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleDownload(doc.bucket_name, doc.file_name);
                                    }}
                                >
                                    <Download size={16} /> Download
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* ── No results ── */}
            {searched && phase === 'done' && sources.length === 0 && !ragAnswer && (
                <div className="search-empty-state">
                    <p className="empty-hint">No matching documents found. Try uploading some documents first.</p>
                </div>
            )}

            {/* ── Empty state ── */}
            {!searched && (
                <div className="search-empty-state">
                    <div className="ai-search-hint">
                        <Sparkles size={20} className="ai-hint-icon" />
                        <p>Ask a question in plain English — the system retrieves relevant documents,
                            then Gemini synthesizes a direct answer from their content.</p>
                    </div>
                    <p className="empty-hint">
                        💡 Try: <em>&quot;what was our Q3 revenue?&quot;</em> · <em>&quot;find contract termination clauses&quot;</em> · <em>&quot;what&apos;s on the product roadmap?&quot;</em>
                    </p>
                </div>
            )}
        </div>
    );
}
