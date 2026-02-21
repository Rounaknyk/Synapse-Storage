'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { Download, RefreshCw, Loader2, FileText, Trash2, Eye } from 'lucide-react';
import { api, DocumentItem } from '@/lib/api';
import { useToast } from './Toast';
import ConfirmModal from './ConfirmModal';

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

type Filter = 'all' | 'finance' | 'legal' | 'general';

function formatDate(iso: string) {
    try { return new Date(iso).toLocaleString(); } catch { return iso; }
}

export default function DocumentList({ refreshKey }: { refreshKey?: number }) {
    const { addToast } = useToast();
    const [docs, setDocs] = useState<DocumentItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<Filter>('all');
    const [deleteModal, setDeleteModal] = useState<{ isOpen: boolean; doc?: DocumentItem }>({ isOpen: false });

    const fetchDocs = useCallback(async () => {
        setLoading(true);
        try {
            const { documents } = await api.listDocuments();
            setDocs(documents);
        } catch {
            addToast('error', 'Failed to load documents.');
        } finally {
            setLoading(false);
        }
    }, [addToast]);

    useEffect(() => { fetchDocs(); }, [fetchDocs, refreshKey]);

    const handleView = async (bucket: string, fileName: string) => {
        try {
            const { download_url } = await api.getDownloadUrl(bucket, fileName);
            window.open(download_url, '_blank');
        } catch {
            addToast('error', 'Failed to open file.');
        }
    };

    const handleDownload = async (bucket: string, fileName: string) => {
        try {
            const { download_url } = await api.getDownloadUrl(bucket, fileName);
            // Create a temporary link to trigger download
            const link = document.createElement('a');
            link.href = download_url;
            link.download = fileName;
            link.click();
        } catch {
            addToast('error', 'Download failed.');
        }
    };

    const openDeleteModal = (doc: DocumentItem) => {
        setDeleteModal({ isOpen: true, doc });
    };

    const closeDeleteModal = () => {
        setDeleteModal({ isOpen: false, doc: undefined });
    };

    const handleDelete = async () => {
        if (!deleteModal.doc) return;
        
        try {
            await api.deleteDocument(deleteModal.doc.bucket_name, deleteModal.doc.file_name);
            addToast('success', `Deleted ${deleteModal.doc.file_name}`);
            fetchDocs(); // Refresh the list
        } catch (error) {
            addToast('error', 'Failed to delete document.');
        }
    };

    const filtered = filter === 'all' ? docs : docs.filter((d) => d.document_type === filter);

    const counts: Record<string, number> = { all: docs.length };
    docs.forEach((d) => { counts[d.document_type] = (counts[d.document_type] || 0) + 1; });

    return (
        <>
            <div className="doclist-wrapper">
                <div className="doclist-header">
                    <div className="filter-chips">
                        {(['all', 'finance', 'legal', 'general'] as Filter[]).map((f) => (
                            <button
                                key={f}
                                className={`filter-chip ${filter === f ? 'filter-chip-active' : ''} filter-chip-${f}`}
                                onClick={() => setFilter(f)}
                            >
                                {f === 'all' ? '📁' : TYPE_ICONS[f]} {f.charAt(0).toUpperCase() + f.slice(1)}
                                <span className="filter-count">{counts[f] || 0}</span>
                            </button>
                        ))}
                    </div>
                    <button className="btn btn-ghost refresh-btn" onClick={fetchDocs} disabled={loading}>
                        <RefreshCw size={16} className={loading ? 'spin' : ''} />
                    </button>
                </div>

                {loading ? (
                    <div className="doclist-loading">
                        <Loader2 size={32} className="spin" />
                        <p>Loading documents…</p>
                    </div>
                ) : filtered.length === 0 ? (
                    <div className="doclist-empty">
                        <FileText size={48} className="empty-icon" />
                        <p>No documents found.</p>
                        <p className="empty-hint">Upload a file to get started!</p>
                    </div>
                ) : (
                    <div className="docgrid">
                        {filtered.map((doc, idx) => (
                            <div key={idx} className="doc-card glass-card">
                                <div className="doc-card-actions">
                                    <button
                                        className="doc-action-btn doc-action-download"
                                        onClick={() => handleDownload(doc.bucket_name, doc.file_name)}
                                        title="Download"
                                    >
                                        <Download size={16} />
                                    </button>
                                    <button
                                        className="doc-action-btn doc-action-delete"
                                        onClick={() => openDeleteModal(doc)}
                                        title="Delete"
                                    >
                                        <Trash2 size={16} />
                                    </button>
                                </div>
                                <div className="doc-card-icon">
                                    {TYPE_ICONS[doc.document_type] || '📄'}
                                </div>
                                <div className="doc-card-body">
                                    <p className="doc-filename">{doc.file_name}</p>
                                    <span className={`badge ${BADGE_CLASS[doc.document_type] || 'badge-general'}`}>
                                        {doc.document_type}
                                    </span>
                                    <p className="doc-time">🕐 {formatDate(doc.upload_time)}</p>
                                </div>
                                <button
                                    className="btn btn-outline doc-view-btn"
                                    onClick={() => handleView(doc.bucket_name, doc.file_name)}
                                >
                                    <Eye size={14} />
                                    View File
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <ConfirmModal
                isOpen={deleteModal.isOpen}
                onClose={closeDeleteModal}
                onConfirm={handleDelete}
                title="Delete Document"
                message={`Are you sure you want to delete "${deleteModal.doc?.file_name}"? This action cannot be undone.`}
                confirmText="Delete"
                confirmStyle="danger"
            />
        </>
    );
}
