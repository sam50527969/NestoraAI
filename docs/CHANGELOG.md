# Nestora AI Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog and follows semantic versioning where practical.

---

# v0.4.2 (In Development)

## Added

### CRM Dashboard

- Added dedicated CRM page foundation.
- Added saved leads table component.
- Added CRM toolbar component.
- Added search across saved lead fields.
- Added category filter for saved leads.
- Added total and visible lead counter.
- Added loading, empty, and error states.
- Added default New status badge foundation.

## Changed

- CRM flow now supports viewing saved leads after they are saved from lead discovery.
- Frontend CRM components are separated into reusable page, toolbar, and table modules.

## Testing

Pending local frontend route verification and end-to-end CRM dashboard testing.

---

# v0.4.1

## Added

### Frontend CRM Integration

- Added Save button behavior to lead table.
- Connected Save button to saveLead() API service.
- Added row-level saving state.
- Added row-level saved state.
- Added row-level save failure message.

---

# v0.4.0

## Added

### Project Foundation

- Created modular React frontend
- Created modular FastAPI backend
- Added GitHub version control
- Added project documentation
- Added PROJECT_STATUS.md
- Added MASTER_CONTEXT.md

### Frontend

- Dashboard page
- KPI cards
- Sidebar navigation
- Top bar
- Lead search form
- Lead table
- React Router
- API service layer

### Backend

- FastAPI application
- Modular route structure
- Configuration module
- Business search service
- OpenStreetMap integration

### CRM

- SQLite database
- SQLAlchemy integration
- Database initialization
- Lead model
- Save Lead API
- Get Saved Leads API

### Infrastructure

- Environment configuration
- Requirements management
- Git workflow

---

## Changed

- Refactored frontend to use a centralized API service layer.
- Reorganized backend into a modular architecture.
- Added React Router navigation.
- Improved project folder structure.

---

## Fixed

- Backend routing issues.
- API communication between frontend and backend.
- Database initialization.
- Python environment compatibility.
- Windows Application Control issues with Python packages.
