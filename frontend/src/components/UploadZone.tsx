'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileText, CheckCircle, XCircle, X } from 'lucide-react';
import { api, BatchUploadResponse } from '@/lib/api';
import { useToast } from './Toast';

const TYPE_COLORS: Record<string, string> = {
    finance: 'badge-finance',
    legal: 'badge-legal',
    general: 'badge-general',
};

const TYPE_ICONS: Record<string, string> = {
    finance: '💰',
    legal: '⚖️',
    general: '📄',
};

export default function UploadZone({ onUploadSuccess }: { onUploadSuccess?: () => void }) {
    const { addToast } = useToast();
    const [progress, setProgress] = useState(0);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState<BatchUploadResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

    const onDrop = useCallback((accepted: File[]) => {
        if (accepted.length > 0) {
            setSelectedFiles((prev) => [...prev, ...accepted]);
            setResult(null);
            setError(null);
        }
    }, []);

    const removeFile = (index: number) => {
        setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'text/plain': ['.txt'],
            'text/markdown': ['.md'],
        },
        multiple: true,
    });

    const handleUpload = async () => {
        if (selectedFiles.length === 0) return;
        setUploading(true);
        setProgress(0);
        setError(null);
        setResult(null);

        try {
            const res = await api.uploadBatch(selectedFiles, setProgress);
            setResult(res);
            if (res.successful > 0) {
                addToast('success', `${res.successful} file(s) uploaded successfully!`);
                onUploadSuccess?.();
            }
            if (res.failed > 0) {
                addToast('warning', `${res.failed} file(s) failed to upload.`);
            }
            setSelectedFiles([]);
        } catch (err: unknown) {
            const msg =
                err instanceof Error ? err.message : 'Upload failed. Please try again.';
            setError(msg);
            addToast('error', msg);
        } finally {
            setUploading(false);
            setProgress(0);
        }
    };

    return (
        <div className="upload-zone-wrapper">
            <div
                {...getRootProps()}
                className={`dropzone ${isDragActive ? 'dropzone-active' : ''} ${selectedFiles.length > 0 ? 'dropzone-has-file' : ''}`}
            >
                <input {...getInputProps()} />
                <div className="dropzone-content">
                    <UploadCloud className={`dropzone-icon ${isDragActive ? 'dropzone-icon-active' : ''}`} size={48} />
                    {isDragActive ? (
                        <p className="dropzone-text">Drop files here!</p>
                    ) : selectedFiles.length > 0 ? (
                        <div className="dropzone-file-info">
                            <FileText size={20} />
                            <span>{selectedFiles.length} file{selectedFiles.length > 1 ? 's' : ''} selected</span>
                            <span className="dropzone-file-size">
                                ({(selectedFiles.reduce((acc, f) => acc + f.size, 0) / 1024).toFixed(1)} KB total)
                            </span>
                        </div>
                    ) : (
                        <>
                            <p className="dropzone-text">Drag &amp; drop files here</p>
                            <p className="dropzone-subtext">or click to browse — PDF, TXT, MD supported · Multiple files allowed</p>
                        </>
                    )}
                </div>
            </div>

            {selectedFiles.length > 0 && !uploading && !result && (
                <div className="selected-files-list">
                    {selectedFiles.map((file, idx) => (
                        <div key={idx} className="selected-file-item">
                            <FileText size={16} />
                            <span className="file-name">{file.name}</span>
                            <span className="file-size">({(file.size / 1024).toFixed(1)} KB)</span>
                            <button
                                className="remove-file-btn"
                                onClick={() => removeFile(idx)}
                                type="button"
                            >
                                <X size={14} />
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {selectedFiles.length > 0 && !uploading && !result && (
                <button className="btn btn-primary upload-btn" onClick={handleUpload}>
                    <UploadCloud size={18} />
                    Upload {selectedFiles.length} File{selectedFiles.length > 1 ? 's' : ''} &amp; Classify
                </button>
            )}

            {uploading && (
                <div className="progress-wrapper">
                    <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${progress}%` }} />
                    </div>
                    <span className="progress-label">{progress}%</span>
                </div>
            )}

            {result && (
                <div className="upload-result-batch">
                    <div className="batch-summary">
                        <CheckCircle size={20} className="result-icon-success" />
                        <p><strong>{result.successful}</strong> of <strong>{result.total_files}</strong> files uploaded successfully</p>
                    </div>
                    
                    {result.results.length > 0 && (
                        <div className="batch-results">
                            <p className="batch-section-title">✅ Successful:</p>
                            {result.results.map((r, idx) => (
                                <div key={idx} className="result-details">
                                    <p className="result-filename">{r.file_name}</p>
                                    <div className="result-meta">
                                        <span className={`badge ${TYPE_COLORS[r.document_type] || 'badge-general'}`}>
                                            {TYPE_ICONS[r.document_type]} {r.document_type}
                                        </span>
                                        <span className="result-bucket">→ {r.bucket_name}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                    
                    {result.errors.length > 0 && (
                        <div className="batch-errors">
                            <p className="batch-section-title">❌ Failed:</p>
                            {result.errors.map((err, idx) => (
                                <div key={idx} className="error-item">
                                    <XCircle size={16} />
                                    <span><strong>{err.file_name}:</strong> {err.error}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {error && (
                <div className="upload-error">
                    <XCircle size={18} />
                    <span>{error}</span>
                </div>
            )}
        </div>
    );
}
