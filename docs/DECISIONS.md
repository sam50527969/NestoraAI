# Nestora AI - Engineering Decisions

Last Updated

2026-07-05

---

# Purpose

This document records important technical and architectural decisions made during development.

Unlike CHANGELOG.md, this document explains WHY decisions were made rather than WHAT changed.

---

# Decision 001

Title

FastAPI as Backend Framework

Status

Accepted

Reason

FastAPI provides:

- Excellent performance
- Automatic Swagger documentation
- Easy REST API creation
- Modern async support
- Excellent AI ecosystem compatibility

Alternative Considered

- Django
- Flask

Decision

Use FastAPI.

---

# Decision 002

Title

React + Vite

Status

Accepted

Reason

Chosen because:

- Very fast startup
- Excellent developer experience
- Easy component architecture
- Modern JavaScript tooling

Alternative

Create React App

Decision

Use React with Vite.

---

# Decision 003

Title

SQLite for Initial Development

Status

Accepted

Reason

SQLite requires no installation.

Benefits

- Zero configuration
- Easy backups
- Portable
- Perfect during early development

Future

Production will migrate to PostgreSQL.

---

# Decision 004

Title

Service-Oriented Backend

Status

Accepted

Reason

Business logic should remain inside services instead of routes.

Benefits

- Cleaner code
- Easier testing
- Better scalability

Structure

Routes

↓

Services

↓

Database

---

# Decision 005

Title

OpenStreetMap Instead of Google Places

Status

Accepted

Reason

Google Places API becomes expensive with high request volumes.

Benefits

- Free
- No billing
- Unlimited experimentation
- Open data

Future

Google Places can become an optional premium provider.

---

# Decision 006

Title

Complete File Replacements During Development

Status

Accepted

Reason

Reduces copy/paste mistakes.

Benefits

- Faster development
- Fewer syntax errors
- Easier for beginner developers

---

# Decision 007

Title

Documentation First

Status

Accepted

Reason

The project will eventually become very large.

Documentation keeps development organized and makes it easy to resume work.

Current Documents

- README.md
- MASTER_CONTEXT.md
- PROJECT_STATUS.md
- CHANGELOG.md
- SESSION_HANDOFF.md
- DECISIONS.md

---

# Decision 008

Title

API-First Architecture

Status

Accepted

Reason

Every feature should be exposed through APIs.

Benefits

- Web frontend
- Mobile app
- AI agents
- Third-party integrations

can all use the same backend.

---

# Decision 009

Title

Modular Folder Structure

Status

Accepted

Backend

app/

routes/

services/

schemas/

database/

models/

Frontend

components/

pages/

services/

assets/

Decision

Keep modules independent.

---

# Decision 010

Title

Nestora Vision

Status

Accepted

Goal

Nestora is not a CRM.

Nestora is an AI Business Operating System.

Future modules include:

- AI CEO
- AI Sales Manager
- AI Marketing Manager
- AI Finance Manager
- AI Research Agent
- AI HR
- AI Customer Support
- AI Automation
- AI Content Studio
- AI Analytics

The CRM is only one component.

---

# Future Decisions

This section is intentionally left empty.

Every major architectural decision should be added here before implementation.

Examples

- PostgreSQL migration
- Docker deployment
- Redis caching
- AI memory system
- Multi-user authentication
- Stripe billing
- SaaS subscriptions
- Agent orchestration
- MCP integration
