# Product Roadmap — 2025

## Vision
Build the world's most intuitive AI-powered document management platform that understands
context, not just keywords.

## Q1 2025 — Foundation
- [x] Semantic search engine using vector embeddings
- [x] Multi-bucket document storage (MinIO)
- [x] Auto-classification (finance / legal / general)
- [ ] Mobile-responsive web UI

## Q2 2025 — Intelligence
- [ ] AI-powered query rewriting (Gemini integration)
- [ ] Document preview snippets in search results
- [ ] Batch upload support (up to 20 files)
- [ ] Support for DOCX, XLSX, CSV, PPTX formats

## Q3 2025 — Collaboration
- [ ] Multi-user support with role-based access
- [ ] Document sharing via secure links
- [ ] Version history and audit trail
- [ ] Slack / Teams integration for document notifications

## Q4 2025 — Scale
- [ ] Kubernetes deployment for auto-scaling
- [ ] Multi-region storage replication
- [ ] SSO integration (Google, Okta)
- [ ] Enterprise analytics dashboard

## Key Performance Indicators
- Search query accuracy: >85% relevance score
- Upload processing time: <3 seconds per document
- System uptime: 99.9% SLA
- User adoption: 500 active users by Q4

## Tech Stack
- Backend: FastAPI, ChromaDB, MinIO, Python 3.12
- AI: Sentence-Transformers (all-MiniLM-L6-v2), Google Gemini
- Frontend: Next.js 14, TypeScript
- Infrastructure: Docker, Kubernetes
