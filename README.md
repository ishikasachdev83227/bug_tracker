# IssueHub

IssueHub is a lightweight bug tracker built for assignment requirements: authentication, project/team management, issue tracking, comments, role-based access, and a React + Python stack.

## 1. Tech Choices And Trade-offs

### Backend
- FastAPI
  - Why: Fast development, built-in OpenAPI docs (`/docs`), strong typing with Pydantic.
  - Trade-off: Requires more discipline on module structure as the app grows.
- SQLAlchemy ORM
  - Why: Clear model layer and DB portability (SQLite locally, PostgreSQL-ready).
  - Trade-off: Relationship loading/permissions need explicit care to avoid subtle bugs.
- Alembic
  - Why: Versioned database migrations for repeatable schema changes.
  - Trade-off: Extra migration management overhead vs direct `create_all`.
- JWT auth (Bearer token)
  - Why: Stateless API auth and easy frontend integration.
  - Trade-off: No server-side token revocation list in current implementation.

### Frontend
- React + Vite + React Router
  - Why: Fast dev server, simple routing, low setup friction.
  - Trade-off: App currently uses local component state instead of a centralized data layer.

### Database
- SQLite (default for local)
  - Why: Zero external setup, very fast to start.
  - Trade-off: Not ideal for heavy concurrent production workloads.
- PostgreSQL-ready
  - Why: Production path is open by changing `DATABASE_URL`.

## 2. Architecture Summary

### Roles
- `maintainer`
  - Can manage team members in projects they maintain.
  - Can create issues in maintained projects.
  - Can change issue status and assignee.
- `member`
  - Can view issues in projects they belong to.
  - Can comment.
  - Cannot create projects or create issues.

### Core Entities
- `users`
- `projects`
- `project_members`
- `issues`
- `comments`

### API Style
- REST JSON under `/api/...`
- Structured error format (`{error: {code, message, details?}}`)

## 3. Setup Instructions

## Prerequisites
- Python `3.11` recommended
- Node.js `18+`
- PowerShell or terminal with script execution enabled

### Environment Variables (backend)
Copy env file:
```powershell
cd backend
copy .env.example .env
```

Variables in `.env`:
- `DATABASE_URL` (default `sqlite:///./issuehub.db`)
- `JWT_SECRET`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

## 4. Database And Migrations

From `backend`:
```powershell
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

Optional demo seed:
```powershell
python scripts/seed.py
```

Reset + reseed:
```powershell
python scripts/seed.py --reset
```

## 5. How To Run

### Backend
```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install email-validator
alembic upgrade head
python -m uvicorn app.main:app --reload --host localhost --port 8000
```

Backend URLs:
- API docs: `http://localhost:8000/docs`
- OpenAPI: `http://localhost:8000/openapi.json`

### Frontend
```powershell
cd frontend
npm install
npm run dev -- --host localhost --port 5173
```

Frontend URL:
- `http://localhost:5173`

## 6. How To Run Tests

### Backend tests
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest
```

Current suite covers auth, role restrictions, membership management, filters, and onboarding endpoints.

## 7. API Overview

### Auth
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/me`

### Projects / Teams
- `POST /api/projects`
- `GET /api/projects`
- `GET /api/projects/maintained`
- `POST /api/projects/{id}/members`
- `POST /api/projects/{id}/members/onboard`
- `GET /api/projects/{id}/members`
- `PATCH /api/projects/{id}/members/{user_id}`
- `DELETE /api/projects/{id}/members/{user_id}`

### Issues / Comments
- `GET /api/projects/{id}/issues`
- `POST /api/projects/{id}/issues`
- `GET /api/issues/{issue_id}`
- `PATCH /api/issues/{issue_id}`
- `DELETE /api/issues/{issue_id}`
- `GET /api/issues/{issue_id}/comments`
- `POST /api/issues/{issue_id}/comments`

## 8. Known Limitations

- Frontend state is local; no dedicated caching/query layer.
- No real email sending for invitations/onboarding.
- JWT session invalidation/refresh flow is minimal.
- UI is functional but not fully polished for production-scale UX.
- Role model is intentionally simple (`member`, `maintainer`) with no org/global admin hierarchy.

## 9. What I Would Do With More Time

1. Add refresh-token flow and logout token revocation.
2. Add richer role matrix and per-action audit logs.
3. Add stronger test coverage (edge cases, contract tests, E2E UI tests).
4. Add async task queue for real invite emails and notifications.
5. Improve pagination UX with server total counts.
6. Add observability (structured logs, request IDs, metrics).
7. Add Docker Compose for one-command local startup.
8. Improve UI/UX consistency and accessibility.
