# Nestora AI - Master Context

## Project

Nestora AI is an AI-powered Business Operating System designed to help entrepreneurs discover leads, manage customers, automate sales, and run businesses using specialized AI agents.

Primary market:
Small and medium businesses in Qatar initially, then GCC and worldwide.

---

# Owner

Project Owner: Sam

Development Assistant: ChatGPT

ChatGPT acts as:

- Lead Software Architect
- Senior Full Stack Engineer
- AI Systems Architect
- Product Manager
- Technical Mentor

---

# Vision

Build a commercial SaaS platform that combines:

- CRM
- Lead Generation
- AI Agents
- Marketing Automation
- Business Intelligence
- CEO Dashboard
- Analytics

The finished product should be something that can realistically be sold as a SaaS platform.

---

# Tech Stack

## Frontend

- React
- Vite
- React Router

Future

- Tailwind CSS
- React Query

---

## Backend

- FastAPI
- Python
- SQLAlchemy
- SQLite

Future

- PostgreSQL
- Redis
- Celery

---

## AI

Future

- OpenAI
- Anthropic Claude
- Local LLM support

---

# Folder Structure

frontend/

components/

pages/

services/

hooks/

utils/

backend/

app/

routes/

services/

database/

models/

schemas/

agents/

core/

docs/

---

# Completed Features

## Frontend

✓ Dashboard

✓ KPI Cards

✓ Sidebar

✓ TopBar

✓ React Router

✓ API Service Layer

✓ Lead Search Form

✓ Lead Table

---

## Backend

✓ FastAPI

✓ Modular Services

✓ Routes

✓ Config

✓ OpenStreetMap Search

✓ Business Search API

---

## CRM

✓ SQLite configured

✓ SQLAlchemy configured

✓ Database created

✓ POST /crm/leads

✓ GET /crm/leads

---

## Infrastructure

✓ GitHub Repository

✓ Git Workflow

✓ PROJECT_STATUS.md

✓ Versioning Strategy

---

# Current Version

v0.4 (Development)

---

# Current Sprint

Sprint 4

CRM Development

---

# Current Status

Completed

- Database
- SQLAlchemy
- CRM API
- Save Lead API
- Get Saved Leads API

Next Task

Connect frontend Save button to CRM.

---

# Development Rules

1.

Always replace complete files instead of partial snippets whenever practical.

2.

Work in small packages.

Each package should include:

- Files changed
- Testing steps
- Git commit message

3.

Always test before moving to the next package.

4.

Keep architecture clean.

Never place business logic inside React components if it belongs in services.

5.

Prefer reusable code.

6.

Every completed package should be committed to Git.

---

# Coding Style

Frontend

- Functional React Components

- Hooks

- Service Layer

Backend

- Routes

- Services

- Database

- Models

- Schemas

Business logic belongs inside services.

---

# Planned AI Agents

CEO Agent

Research Agent

Sales Agent

Marketing Agent

Finance Agent

Operations Agent

Automation Agent

Customer Support Agent

---

# Product Roadmap

v0.4

CRM

Lead Saving

Lead Editing

Lead Notes

v0.5

AI CEO

Lead Scoring

Daily Recommendations

v0.6

Sales Agent

Email Generator

WhatsApp Generator

Cold Call Script

v0.7

Marketing

Ads

Social Posts

Content Generation

v0.8

Finance

Revenue

Profit

Forecasting

v0.9

Automation

Scheduling

Notifications

Follow-ups

v1.0

Public Beta

---

# Long-Term Objective

Create one of the best AI-powered Business Operating Systems for entrepreneurs.

The software should eventually be able to operate a business with minimal human intervention.

---

# Working Style

ChatGPT should behave as the project's Lead Software Architect.

Recommendations should prioritize:

- Maintainability
- Scalability
- Professional architecture
- Commercial readiness

Every new feature should be designed as if the product will eventually have thousands of users.

---

# Session Resume Prompt

When starting a new chat, use:

"Read MASTER_CONTEXT.md and PROJECT_STATUS.md.

Continue building Nestora AI from the latest completed sprint.

Do not restart the project.

Continue exactly from the current architecture."