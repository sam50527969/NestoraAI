# Nestora AI

## Vision

Nestora AI is an AI-powered Business Operating System designed to help entrepreneurs discover opportunities, generate leads, manage customers, automate sales, and run businesses using specialized AI agents.

The goal is not to build another CRM.

The goal is to build an AI workforce.

---

# Current Version

v0.4.2 (Development)

---

# Current Sprint

Sprint 4

CRM Development

---

# Completed Packages

## Package 4.0

CRM Backend

Status: Completed

Completed:

- SQLite database
- SQLAlchemy integration
- Database initialization
- Lead model
- POST /crm/leads
- GET /crm/leads
- Swagger CRM endpoint testing

## Package 4.1

Frontend Save Lead Integration

Status: Completed

Completed:

- Save button added to each lead row
- Save button calls CRM backend through saveLead()
- Save button disables during save request
- Saved leads show a Saved state
- Save failures show a row-level error message
- Existing Google Maps and lead table behavior preserved

## Package 4.2

CRM Dashboard

Status: Ready for Testing

Completed:

- CRM page created
- CRM table component created
- CRM toolbar component created
- Saved leads loaded from getSavedLeads()
- Search by lead text
- Category filter
- Lead counter
- Loading, empty, and error states
- Status badge foundation

---

# Completed

## Frontend

- React + Vite
- React Router
- Dashboard
- Sidebar Navigation
- KPI Cards
- Lead Search Form
- Lead Table
- API Service Layer
- Frontend Save Lead button connected to CRM backend
- CRM Dashboard page foundation
- Saved leads table
- CRM search and category filter

---

## Backend

- FastAPI
- Modular Architecture
- Routes
- Services
- Configuration
- Environment Variables
- CORS
- OpenStreetMap Business Search
- SQLite Database
- SQLAlchemy
- CRM Save Lead API
- CRM Get Saved Leads API

---

## Features

- Live Business Search
- Google Maps Button
- Dynamic Lead Table
- API Integration
- GitHub Version Control
- Professional Sidebar Navigation
- React Router
- Business Search API
- OpenStreetMap Integration
- API Service Layer
- Save searched leads into CRM
- View saved leads in CRM Dashboard

---

# Current Package

Package 4.2

CRM Dashboard

Status: Ready for Local Testing

Testing Required:

- Confirm /crm route is connected in the frontend router
- Confirm saved leads load from backend
- Confirm search works
- Confirm category filter works
- Confirm Refresh reloads saved leads

---

# Next Package

Package 4.3

Lead Details

Planned:

- Add lead detail view
- Add notes foundation
- Prepare backend model fields for status, priority, tags, and assigned user
- Prepare CRM table action column

---

# Architecture

Frontend

React
↓
API Service
↓
FastAPI
↓
Services
↓
Database

---

# AI Agents

CEO Agent

Research Agent

Sales Agent

Marketing Agent

Finance Agent

Operations Agent

Customer Support Agent

Automation Agent

---

# Long-Term Goal

Create the world's best AI-powered Business Operating System for entrepreneurs.
