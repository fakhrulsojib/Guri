# 🤖 PROJECT ARCHITECTURE & AGENT CONTEXT (AGENTS.md)
> **Goal:** High-level system architecture, cross-project boundaries, and source of truth locations for AI-assisted development.

## 🏗️ Repository Structure
This repository contains separated frontend, backend, and machine learning components.

| Path | Environment | Description | Context File |
|---|---|---|---|
| `/frontend` | React, Vite, TS | Web dashboard (Redux, Vitest, ESLint, Prettier, Error Boundaries). | [`.context.md`](./frontend/.context.md) |
| `/server` | FastAPI, Python | Core backend API, logs ingestion endpoints, and data access. | [`.context.md`](./server/.context.md) |
| `/ml` | Python, Scikit-learn, Ollama | Machine learning pipelines, anomaly detection, and RAG services. | [`.context.md`](./ml/.context.md) |

## 🔗 Cross-Project Boundaries
- **API Contract:** Data exchange between `frontend` and `server`/`ml` occurs via REST endpoints and WebSockets defined in the FastAPI application.
- **Event Streaming:** Kafka is used for asynchronous processing and log buffering between services.
- **Separation of Concerns:** The core CRUD back-end is separated from the long-running Machine Learning and AI inference tasks.

## 🧭 Sources of Truth
- **Database Schema:** `/server/model/` directory.
- **Frontend Global State:** Redux slices inside `/frontend/src/store/`.
- **ML Configuration:** `/ml/model_config.py` or `.env` setups.
- **Environment & Deployment:** `docker-compose.yml`, `docker-compose.dev.yml`, and `.env` files at the repository root.

## 🚫 Constraints (AI Rules)
- Do NOT invent undefined root-level directories.
- Do NOT assume Node.js for the backend. The backend is built natively in Python using FastAPI.
- Do NOT bypass standard Kafka ingestion pipelines for log ingestion without justification.
- Do NOT alter database schemas without verifying against the existing models in `/server/model/`.
