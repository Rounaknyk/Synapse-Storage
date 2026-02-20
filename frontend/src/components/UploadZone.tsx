'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileText, CheckCircle, XCircle } from 'lucide-react';
import { api, UploadResult } from '@/lib/api';
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
    const [result, setResult] = useState<UploadResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const onDrop = useCallback((accepted: File[]) => {
        if (accepted.length > 0) {
            setSelectedFile(accepted[0]);
            setResult(null);
            setError(null);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'text/plain': ['.txt'],
            'text/markdown': ['.md'],
        },
        multiple: false,
    });

    const handleUpload = async () => {
        if (!selectedFile) return;
        setUploading(true);
        setProgress(0);
        setError(null);
        setResult(null);

        try {
            const res = await api.uploadFile(selectedFile, setProgress);
            setResult(res);
            addToast('success', `Classified as "${res.document_type}" and uploaded!`);
            onUploadSuccess?.();
            setSelectedFile(null);
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
                className={`dropzone ${isDragActive ? 'dropzone-active' : ''} ${selectedFile ? 'dropzone-has-file' : ''}`}
            >
                <input {...getInputProps()} />
                <div className="dropzone-content">
                    <UploadCloud className={`dropzone-icon ${isDragActive ? 'dropzone-icon-active' : ''}`} size={48} />
                    {isDragActive ? (
                        <p className="dropzone-text">Drop it here!</p>
                    ) : selectedFile ? (
                        <div className="dropzone-file-info">
                            <FileText size={20} />
                            <span>{selectedFile.name}</span>
                            <span className="dropzone-file-size">
                                ({(selectedFile.size / 1024).toFixed(1)} KB)
                            </span>
                        </div>
                    ) : (
                        <>
                            <p className="dropzone-text">Drag &amp; drop a file here</p>
                            <p className="dropzone-subtext">or click to browse — PDF, TXT, MD supported</p>
                        </>
                    )}
                </div>
            </div>

            {selectedFile && !uploading && !result && (
                <button className="btn btn-primary upload-btn" onClick={handleUpload}>
                    <UploadCloud size={18} />
                    Upload &amp; Classify
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
                <div className="upload-result">
                    <CheckCircle size={20} className="result-icon-success" />
                    <div className="result-details">
                        <p className="result-filename">{result.file_name}</p>
                        <div className="result-meta">
                            <span className={`badge ${TYPE_COLORS[result.document_type] || 'badge-general'}`}>
                                {TYPE_ICONS[result.document_type]} {result.document_type}
                            </span>
                            <span className="result-bucket">Bucket: {result.bucket_name}</span>
                        </div>
                    </div>
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
