# API Specification
## Multi-Tenant Project Management API

| Field    | Value       |
|----------|-------------|
| Version  | 0.1 (Draft) |
| Base URL | /api/v1     |

All endpoints are prefixed with `/api/v1`. Request and response bodies are JSON.
Authenticated endpoints require a valid access token sent in the request's
`Authorization` header.

---

## 1. Authentication

Authentication endpoints are action-oriented rather than resource-oriented — a
deliberate, normal exception to REST, since "log in" is a verb, not a resource.

| Method | Path                  | Purpose                                    | Auth | Success |
|--------|-----------------------|--------------------------------------------|------|---------|
| POST   | /auth/register        | Create a new user account                  | None | 201     |
| POST   | /auth/login           | Authenticate; receive tokens               | None | 200     |
| POST   | /auth/refresh         | Exchange a refresh token for a new access token | None | 200 |
| POST   | /auth/logout          | Invalidate the current session             | Yes  | 204     |
| POST   | /auth/forgot-password | Request a password-reset token             | None | 200     |
| POST   | /auth/reset-password  | Set a new password using a reset token     | None | 200     |
| GET    | /auth/me              | Get the current authenticated user         | Yes  | 200     |

### Key request / response shapes

- **POST /auth/register** — body `{ email, password, full_name }`. Returns the
  created user `{ id, email, full_name, created_at }`. The password hash is never
  returned. Email must be unique; a duplicate returns `409 Conflict`.
- **POST /auth/login** — body `{ email, password }`. Returns
  `{ access_token, refresh_token }`. Invalid credentials return `401` with a
  generic message (SRS FR-1.3): the error never reveals whether the email or the
  password was wrong.
- **POST /auth/forgot-password** — body `{ email }`. Always returns `200`, even
  when the email is not registered, so the endpoint cannot be used to discover
  which emails have accounts.
- **POST /auth/reset-password** — body `{ token, new_password }`. The reset token
  is single-use and time-limited (SRS FR-1.6).
- **GET /auth/me** — returns the current user; the identity comes from the access
  token, not from any input.

  ---

## 2. Organizations

| Method | Path                  | Purpose                        | Who can do it        | Success |
|--------|-----------------------|--------------------------------|----------------------|---------|
| POST   | /organizations        | Create an organization         | Any logged-in user   | 201     |
| GET    | /organizations        | List orgs the user belongs to  | Any member           | 200     |
| GET    | /organizations/{id}   | Get one organization           | Member of that org   | 200     |
| PATCH  | /organizations/{id}   | Update org details (e.g. name) | Owner or Admin       | 200     |
| DELETE | /organizations/{id}   | Delete an organization         | Owner only           | 204     |

- **POST /organizations** — body `{ name }`. The creator is automatically made the
  Owner (SRS FR-2.1): the server creates the organization *and* an
  organization_membership row with role OWNER, in one operation.
- **GET /organizations** — returns only the organizations the requesting user is a
  member of (SRS FR-2.2, tenant isolation). It never lists organizations the user
  doesn't belong to.
- **DELETE /organizations/{id}** — cascades: deleting an org removes its
  memberships, projects, tasks, and comments (SRS FR-2.5).

## 3. Organization Members & Invitations

| Method | Path                                      | Purpose                          | Who can do it     | Success |
|--------|-------------------------------------------|----------------------------------|-------------------|---------|
| GET    | /organizations/{id}/members               | List members and their roles     | Member of the org | 200     |
| POST   | /organizations/{id}/invitations           | Invite someone by email          | Owner or Admin    | 201     |
| GET    | /organizations/{id}/invitations           | List pending invitations         | Owner or Admin    | 200     |
| POST   | /invitations/{token}/accept               | Accept an invitation             | Invited user      | 200     |
| PATCH  | /organizations/{id}/members/{user_id}     | Change a member's role           | Owner or Admin    | 200     |
| DELETE | /organizations/{id}/members/{user_id}     | Remove a member from the org     | Owner or Admin    | 204     |

- **POST /organizations/{id}/invitations** — body `{ email, role }`. Creates a
  pending invitation and (per SRS) sends an invitation email containing a unique
  token. If the invited person accepts, they become a member with the given role.
- **POST /invitations/{token}/accept** — the invited user accepts via the token
  from their email. On success, an organization_membership row is created linking
  that user to the org with the invited role.
- **PATCH .../members/{user_id}** — body `{ role }`. Changes a member's org-level
  role, subject to the rule that an org always has exactly one Owner (SRS FR-2.6).

  ---

## 4. Projects

Projects live inside an organization, so they are nested under it. A user must be a
member of the organization to touch its projects at all, and project-level
visibility then depends on their role.

| Method | Path                                   | Purpose                     | Who can do it                          | Success |
|--------|----------------------------------------|-----------------------------|----------------------------------------|---------|
| POST   | /organizations/{org_id}/projects       | Create a project            | Org Owner or Admin                     | 201     |
| GET    | /organizations/{org_id}/projects       | List projects the user sees | Org members (see visibility rule)      | 200     |
| GET    | /projects/{id}                         | Get one project             | Project member, or org Owner/Admin     | 200     |
| PATCH  | /projects/{id}                         | Update project details      | Project Admin, or org Owner/Admin      | 200     |
| DELETE | /projects/{id}                         | Delete a project            | Project Admin, or org Owner/Admin      | 204     |

- **GET /organizations/{org_id}/projects** — visibility rule (SRS FR-3.3): an org
  Owner or Admin sees *all* projects in the org; a plain Member sees *only* the
  projects they have been added to.
- **POST /organizations/{org_id}/projects** — body `{ name, description }`. The
  project is created inside the given organization.
- **DELETE /projects/{id}** — cascades: deleting a project removes its tasks and
  comments (SRS FR-3.5).

## 5. Project Members

| Method | Path                                        | Purpose                     | Who can do it                      | Success |
|--------|---------------------------------------------|-----------------------------|------------------------------------|---------|
| GET    | /projects/{id}/members                       | List project members        | Project member, or org Owner/Admin | 200     |
| POST   | /projects/{id}/members                        | Add an org member to project | Project Admin, or org Owner/Admin  | 201     |
| PATCH  | /projects/{id}/members/{user_id}              | Change a member's project role | Project Admin, or org Owner/Admin | 200     |
| DELETE | /projects/{id}/members/{user_id}              | Remove a member from project | Project Admin, or org Owner/Admin  | 204     |

- **POST /projects/{id}/members** — body `{ user_id, role }`. The user being added
  must already be a member of the project's organization — you cannot add a total
  outsider directly to a project. This is a business rule the endpoint enforces.

  ---

## 6. Tasks

Tasks live inside projects. Any member of a project can create and work on its
tasks; deletion is restricted. Listing supports filtering, sorting, and pagination.

| Method | Path                          | Purpose                  | Who can do it        | Success |
|--------|-------------------------------|--------------------------|----------------------|---------|
| POST   | /projects/{project_id}/tasks  | Create a task            | Any project member   | 201     |
| GET    | /projects/{project_id}/tasks  | List/filter tasks        | Any project member   | 200     |
| GET    | /tasks/{id}                   | Get one task             | Project member       | 200     |
| PATCH  | /tasks/{id}                   | Update a task            | Any project member   | 200     |
| DELETE | /tasks/{id}                   | Delete a task            | Project Admin        | 204     |

- **POST /projects/{project_id}/tasks** — body `{ title, description?, status?,
  priority?, assignee_id?, due_date? }`. Only `title` is required. If `assignee_id`
  is given, that user must be a member of this project (SRS FR-4.5).
- **PATCH /tasks/{id}** — body contains any subset of the task's fields; only the
  provided fields are changed. `status` and `priority` must be valid enum values,
  else `400`.
- **GET /projects/{project_id}/tasks** — supports query parameters:
  - Filtering: `?status=IN_PROGRESS`, `?assignee_id=7`
  - Sorting: `?sort=due_date` or `?sort=-due_date` (a leading `-` means descending)
  - Pagination: `?page=1&page_size=20`
  - Returns a paginated envelope: `{ items: [...], total, page, page_size }`.

## 7. Comments

Comments live inside tasks. Any project member can comment; a comment can be
deleted by its author or by a Project Admin.

| Method | Path                    | Purpose                    | Who can do it              | Success |
|--------|-------------------------|----------------------------|---------------------------|---------|
| POST   | /tasks/{task_id}/comments | Add a comment to a task    | Any project member        | 201     |
| GET    | /tasks/{task_id}/comments | List comments on a task    | Any project member        | 200     |
| DELETE | /comments/{id}            | Delete a comment           | Comment author, or Project Admin | 204 |

- **POST /tasks/{task_id}/comments** — body `{ body }`. The author is the current
  authenticated user (taken from the token, never from the request body).

## 8. Activity Log

| Method | Path                              | Purpose                          | Who can do it        | Success |
|--------|-----------------------------------|----------------------------------|----------------------|---------|
| GET    | /organizations/{org_id}/activity  | List activity in the org         | Org member (scoped)  | 200     |

- Activity entries are scoped to projects the requesting user can access (SRS
  FR-6.3), and support the same pagination as tasks.

---

## 9. Conventions Summary

- **Auth:** protected endpoints require `Authorization: Bearer <access_token>`.
- **Errors:** failures return a consistent JSON shape, e.g.
  `{ detail: "message" }`, with an appropriate status code.
- **Status codes:** 200 OK, 201 Created, 204 No Content, 400 Bad Request,
  401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict.
- **IDs** in URLs are integers. **Timestamps** are ISO 8601 strings.