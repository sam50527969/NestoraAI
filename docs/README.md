# 🚀 Nestora AI

> **The AI Business Operating System**

Nestora AI is an intelligent business platform designed to help entrepreneurs discover leads, manage customers, automate repetitive work, and eventually run entire businesses using AI agents.

---

# Vision

Nestora is not just a CRM.

It is an AI-powered operating system where specialized AI agents work together to help businesses grow.

Future AI Agents include:

- 🧠 AI CEO
- 💰 AI Sales Manager
- 📈 AI Marketing Manager
- 🔍 AI Research Agent
- 💬 AI Customer Support
- 📊 AI Analytics
- 👨‍💼 AI HR Manager
- 💳 AI Finance Manager
- ✍ AI Content Studio
- 🤖 Workflow Automation

---

# Current Features

## Lead Discovery

- Live business search
- OpenStreetMap integration
- Google Maps links
- Dynamic lead table
- Location search

---

## CRM

- Save leads
- SQLite database
- REST API
- Swagger documentation

(Currently under development)

---

## Dashboard

- AI Dashboard
- KPI cards
- Modern interface
- Sidebar navigation

---

# Technology Stack

## Backend

- FastAPI
- Python
- SQLAlchemy
- SQLite
- REST API

Future

- PostgreSQL
- Redis
- Docker

---

## Frontend

- React
- Vite
- React Router
- Axios
- CSS

---

## AI

Future

- OpenAI
- Anthropic Claude
- MCP
- Local LLM Support

---

# Project Structure

```
NestoraAI/

├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── config.py
│   │
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── assets/
│   │
│   └── package.json
│
└── docs/
    ├── MASTER_CONTEXT.md
    ├── PROJECT_STATUS.md
    ├── CHANGELOG.md
    ├── SESSION_HANDOFF.md
    └── DECISIONS.md
```

---

# Documentation

Project documentation lives inside the **docs** folder.

| Document | Purpose |
|----------|---------|
| MASTER_CONTEXT.md | Long-term project memory |
| PROJECT_STATUS.md | Current progress |
| CHANGELOG.md | Development history |
| SESSION_HANDOFF.md | Resume work in the next session |
| DECISIONS.md | Engineering decisions |

---

# Getting Started

## Backend

```
cd backend

python -m venv venv

venv\Scripts\activate

python -m pip install -r requirements.txt

python -m uvicorn main:app --reload
```

Backend URL

```
http://127.0.0.1:8000
```

Swagger

```
http://127.0.0.1:8000/docs
```

---

## Frontend

```
cd frontend

npm install

npm run dev
```

Frontend

```
http://localhost:5173
```

---

# Development Workflow

1. Update PROJECT_STATUS.md
2. Record changes in CHANGELOG.md
3. Record architecture decisions in DECISIONS.md
4. Update SESSION_HANDOFF.md
5. Commit changes to Git

---

# Roadmap

## Version 0.4

- CRM
- Save Leads
- SQLite

---

## Version 0.5

- CRM Dashboard
- Notes
- Lead Status
- Tags
- Search

---

## Version 0.6

- AI Research Agent
- AI Lead Scoring
- AI Recommendations

---

## Version 0.7

- Marketing Automation
- Email Campaigns
- WhatsApp Integration

---

## Version 0.8

- AI Sales Manager
- Opportunity Tracking
- Sales Pipeline

---

## Version 1.0

Nestora AI Business Operating System

---

# Design Principles

Every feature should be:

- Modular
- Scalable
- API First
- AI Ready
- Easy to Maintain
- Easy to Extend

---

# Current Status

Current Version

```
v0.4
```

Current Sprint

```
Sprint 4
```

Current Focus

```
CRM Development
```

---

# License

Private Project

Copyright © 2026 Nestora AI

All Rights Reserved.