# Development Roadmap
## Multi-Tenant Project Management API

This roadmap sequences the build into phases. Each phase produces something that
runs and can be tested before the next begins. Phases are ordered by dependency:
later phases build on earlier ones.

---

### Phase 0 — Planning (complete)
- [x] Software Requirements Specification
- [x] Database ER diagram
- [x] API specification
- [x] Development roadmap

### Phase 1 — Project Foundation
Goal: a running FastAPI app and a clean, professional project structure.
- Set up a Python virtual environment and dependency management.
- Install FastAPI and create a minimal running app (a health-check endpoint).
- Establish the layered project structure (routers, services, models, schemas).
- Add configuration management via environment variables.
**Done when:** the app starts and `GET /health` returns 200.

### Phase 2 — Database Layer
Goal: the database connected and the schema created from the ER diagram.
- Connect to PostgreSQL via SQLAlchemy.
- Define the ORM models (the eight tables from the ER diagram).
- Set up Alembic and generate the first migration.
- Confirm all tables are created in the database.
**Done when:** migrations run and every table exists.

### Phase 3 — Authentication
Goal: users can register and log in; endpoints can be protected.
- Implement password hashing.
- Implement registration and login, issuing JWT tokens.
- Add the dependency that protects endpoints and identifies the current user.
- Implement refresh, logout, and password reset.
**Done when:** a user can register, log in, and access a protected endpoint.

### Phase 4 — Organizations & Membership
Goal: the multi-tenancy core — organizations, members, roles, invitations.
- Organization CRUD, with the creator becoming Owner.
- The organization-level permission checks (Owner / Admin / Member).
- The invitation flow (invite, accept).
- Enforce tenant isolation everywhere.
**Done when:** a user can create an org, invite others, and isolation holds.

### Phase 5 — Projects & Project Membership
Goal: projects inside organizations, with the second permission tier.
- Project CRUD, nested under organizations.
- Project membership and project-level roles.
- The combined permission checks (project role, falling back to org role).
**Done when:** the two-tier permission model works end to end.

### Phase 6 — Tasks & Comments
Goal: the core collaborative features.
- Task CRUD, with status/priority enums and assignee rules.
- Filtering, sorting, and pagination on task lists.
- Comments on tasks.
- The activity log.
**Done when:** the full task/comment workflow functions.

### Phase 7 — Quality & Hardening
Goal: make it production-grade, not just working.
- Consistent error handling and validation.
- Structured logging.
- Automated tests (unit and integration) with meaningful coverage.
- Security review (headers, rate limiting, CORS).
**Done when:** the test suite passes and the API is robust.

### Phase 8 — Delivery
Goal: containerized, automated, deployed, documented.
- Dockerize the app and database (Docker Compose).
- CI/CD pipeline (automated tests and linting on every push).
- Deploy to a hosting platform.
- Complete the README and documentation.
**Done when:** the project is live, with a green CI badge and full docs.

### Future / Stretch (not committed)
- A web frontend.
- Teams (the third permission tier).
- File attachments on tasks.
- Real email delivery for invitations.