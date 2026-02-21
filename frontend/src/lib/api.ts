import axios from 'axios';
import { auth } from './firebase';

const BASE_URL = 'http://localhost:8000';

const client = axios.create({ baseURL: BASE_URL });

// Automatically attach Firebase ID Token to every request
client.interceptors.request.use(async (config) => {
    const user = auth.currentUser;
    if (user) {
        try {
            const token = await user.getIdToken();
            config.headers.Authorization = `Bearer ${token}`;
        } catch (error) {
            console.error('Error fetching Firebase token:', error);
        }
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

export interface UploadResult {
    success: boolean;
    message?: string;
    file_name: string;
    document_type: 'finance' | 'legal' | 'general';
    bucket_name: string;
}

export interface BatchUploadResponse {
    total_files: number;
    successful: number;
    failed: number;
    results: UploadResult[];
    errors: Array<{ file_name: string; error: string }>;
}

export interface SearchResult {
    file_name: string;
    bucket_name: string;
    document_type: 'finance' | 'legal' | 'general';
    upload_time: string;
    similarity_score: number;
    preview?: string; // Optional text snippet returned by backend
}

export interface SmartSearchResponse {
    query: string;
    rag_answer: string;      // Gemini-generated answer grounded in retrieved docs
    sources: SearchResult[]; // The retrieved documents used as context
}

export interface DocumentItem {
    file_name: string;
    bucket_name: string;
    document_type: 'finance' | 'legal' | 'general';
    upload_time: string;
}

export interface DocumentsResponse {
    total_documents: number;
    documents: DocumentItem[];
}

export interface DownloadResponse {
    file_name: string;
    bucket_name: string;
    download_url: string;
}

export interface DeleteResponse {
    success: boolean;
    message: string;
    file_name: string;
    bucket_name: string;
    deleted_from_search: boolean;
    deleted_from_storage: boolean;
}

export interface BatchDeleteRequest {
    files: Array<{ bucket_name: string; file_name: string }>;
}

export interface BatchDeleteResponse {
    total_files: number;
    successful: number;
    failed: number;
    results: Array<{
        file_name: string;
        bucket_name: string;
        deleted_from_search: boolean;
        deleted_from_storage: boolean;
        success: boolean;
    }>;
}

export const api = {
    async uploadFile(
        file: File,
        onProgress?: (pct: number) => void
    ): Promise<UploadResult> {
        const form = new FormData();
        form.append('file', file);
        const { data } = await client.post<UploadResult>('/upload', form, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (e) => {
                if (onProgress && e.total) {
                    onProgress(Math.round((e.loaded / e.total) * 100));
                }
            },
        });
        return data;
    },

    async uploadBatch(
        files: File[],
        onProgress?: (pct: number) => void
    ): Promise<BatchUploadResponse> {
        const form = new FormData();
        files.forEach((file) => form.append('files', file));
        const { data } = await client.post<BatchUploadResponse>('/upload-batch', form, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (e) => {
                if (onProgress && e.total) {
                    onProgress(Math.round((e.loaded / e.total) * 100));
                }
            },
        });
        return data;
    },

    async searchDocuments(query: string, topK = 5, minSimilarity = 0.0): Promise<SearchResult[]> {
        const { data } = await client.post<SearchResult[]>('/search', {
            query,
            top_k: topK,
            min_similarity: minSimilarity,
        });
        return data;
    },

    async smartSearch(
        query: string,
        topK = 5,
        minSimilarity = 0.0
    ): Promise<SmartSearchResponse> {
        const { data } = await client.post<SmartSearchResponse>('/search/smart', {
            query,
            top_k: topK,
            min_similarity: minSimilarity,
        });
        return data;
    },

    async listDocuments(): Promise<DocumentsResponse> {
        const { data } = await client.get<DocumentsResponse>('/documents');
        return data;
    },

    async getDownloadUrl(bucket: string, fileName: string, inline = false): Promise<{ download_url: string }> {
        const { data } = await client.get(`/download/${bucket}/${fileName}?inline=${inline}`);
        return data;
    },

    async deleteDocument(
        bucketName: string,
        fileName: string
    ): Promise<DeleteResponse> {
        const { data } = await client.delete<DeleteResponse>(
            `/documents/${bucketName}/${fileName}`
        );
        return data;
    },

    async deleteBatch(request: BatchDeleteRequest): Promise<BatchDeleteResponse> {
        const { data } = await client.post<BatchDeleteResponse>(
            '/documents/delete-batch',
            request
        );
        return data;
    },
};
