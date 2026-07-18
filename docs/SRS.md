# Software Requirements Specification (SRS)
## Multi-Tenant Project Management API

| Field   | Value           |
|---------|-----------------|
| Version | 0.1 (Draft)     |
| Date    | 2026-07-18      |
| Author  | Arjun Saxena    |
| Status  | In progress     |

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for the Multi-Tenant Project Management API.
It describes *what* the system must do and the constraints it must satisfy, and serves
as the single source of truth for development, review, and future maintenance. It
deliberately avoids implementation details (*how* the system is built); those belong
in the architecture and design documents.

### 1.2 Product Overview
The system is a backend REST API that lets multiple independent organizations manage
their own projects and tasks in isolation. Each organization is a self-contained
tenant: its members, projects, and data are private to that organization and never
visible to any other. Within an organization, users collaborate on projects and the
tasks inside them, with permissions controlled at both the organization and project
level.

### 1.3 Intended Audience
Developers implementing the system, reviewers assessing it, and any future maintainer
(including the author) who needs to understand the agreed scope and behavior.

---

## 2. Scope

### 2.1 In Scope (MVP)
- **Account authentication:** registration, login, logout, and password reset.
- **Organizations (tenants):** any authenticated user can create an organization and
  becomes its Owner.
- **Membership & invitations:** users are invited by email, must accept to join, and
  are assigned an organization-level role.
- **Projects:** projects belong to an organization; membership and a role are assigned
  per project.
- **Tasks:** tasks belong to a project and have a title, description, status, assignee,
  due date, and priority.
- **Comments:** users can comment on tasks.
- **Activity log:** an audit trail records significant actions (who did what, and when).

### 2.2 Out of Scope
Each exclusion is deliberate; the rationale matters as much as the decision.

- **Real-time updates / WebSockets** — the API is request/response only. Real-time
  collaboration would add significant infrastructure for a feature the core use case
  does not require.
- **Billing & payments** — a distinct concern with its own complexity; excluded.
- **Advanced project management** — sprints, Gantt charts, time tracking, custom fields,
  and configurable workflows are excluded to keep the domain focused.
- **Notifications beyond invitations** — email digests and rich notification systems are
  excluded; only the invitation email is in scope.

### 2.3 Stretch Goals (Not committed)
Documented as possible future work, explicitly not part of the MVP:
- **Teams** — an organizational layer between organizations and projects, adding a third
  permission tier.
- **File attachments on tasks** — would introduce object storage; deferred until the core
  system is complete.

---

## 3. User Roles & Permissions

The system uses a **two-tier permission model**: every user has a role at the
organization level, and — if added to a project — a separate role at the project level.
Project roles layer on top of organization roles; they do not replace them. The precise
interaction between the two tiers (for example, whether an organization Admin
automatically has project access) is defined in the functional requirements.

### 3.1 Organization-Level Roles
- **Owner** — creates the organization; has full control, including deleting it.
  Exactly one Owner per organization (initially).
- **Admin** — manages members and all projects within the organization; cannot delete
  the organization.
- **Member** — can only access projects they have been explicitly added to; cannot see
  other projects or organization-wide settings.

### 3.2 Project-Level Roles
- **Project Admin** — manages a specific project: its settings, members, tasks, and
  comments.
- **Project Contributor** — works within a project: creates and updates tasks and
  comments, but cannot manage project membership or settings.

  ---

## 4. Functional Requirements

Each requirement is written as a specific, testable statement. "Shall" denotes a
mandatory behavior.

### 4.1 Authentication & Accounts

- **FR-1.1 Registration:** The system shall allow a new user to register with an email
  address and a password. Email addresses shall be unique across the system.
- **FR-1.2 Password storage:** The system shall never store passwords in plain text;
  passwords shall be stored only as secure hashes.
- **FR-1.3 Login:** The system shall allow a registered user to log in with their email
  and password, and shall reject invalid credentials with a generic error (not
  revealing whether the email or the password was wrong).
- **FR-1.4 Authenticated sessions:** On successful login, the system shall issue the user
  a token that authenticates their subsequent requests.
- **FR-1.5 Logout:** The system shall allow a logged-in user to log out, invalidating
  their current session.
- **FR-1.6 Password reset:** The system shall allow a user to request a password reset
  for their email, and to set a new password via a time-limited, single-use reset token.
- **FR-1.7 Protected access:** The system shall reject any request to a protected
  resource that does not carry a valid authentication token.

### 4.2 Organizations (Tenants)

- **FR-2.1 Creation:** The system shall allow any authenticated user to create an
  organization. The creating user shall automatically become that organization's Owner.
- **FR-2.2 Tenant isolation:** The system shall ensure that a user can only access data
  belonging to organizations they are a member of. Data from one organization shall never
  be visible to members of another.
- **FR-2.3 Viewing:** The system shall allow a member to view the organizations they
  belong to, and the details of any organization they are a member of.
- **FR-2.4 Updating:** The system shall allow an Owner or Admin to update their
  organization's details (e.g. its name).
- **FR-2.5 Deletion:** The system shall allow only the Owner to delete an organization.
  Deleting an organization shall remove its associated projects, tasks, and memberships.
- **FR-2.6 Role assignment:** The system shall allow an Owner or Admin to change the
  organization-level role of a member, subject to the constraint that an organization
  always has exactly one Owner.

  ### 4.3 Projects

- **FR-3.1 Creation:** The system shall allow an Owner or Admin to create a project
  within their organization. A project shall belong to exactly one organization.
- **FR-3.2 Project membership:** The system shall allow an Owner, Admin, or a project's
  Project Admin to add organization members to a project and assign them a project-level
  role.
- **FR-3.3 Visibility:** The system shall ensure a Member can view only the projects they
  have been added to. Owners and Admins may view all projects in their organization.
- **FR-3.4 Updating:** The system shall allow an Owner, Admin, or Project Admin to update
  a project's details.
- **FR-3.5 Deletion:** The system shall allow an Owner, Admin, or Project Admin to delete
  a project. Deleting a project shall remove its tasks and comments.

### 4.4 Tasks

- **FR-4.1 Creation:** The system shall allow any member of a project to create a task
  within that project. A task shall belong to exactly one project.
- **FR-4.2 Attributes:** A task shall have a title (required), and optionally a
  description, status, assignee, due date, and priority.
- **FR-4.3 Status:** The system shall support a defined set of task statuses (e.g. To Do,
  In Progress, Done) and reject any status outside that set.
- **FR-4.4 Priority:** The system shall support a defined set of priorities (e.g. Low,
  Medium, High) and reject any value outside that set.
- **FR-4.5 Assignment:** The system shall allow a task to be assigned to a member of the
  same project, and shall reject assignment to a user who is not a project member.
- **FR-4.6 Updating:** The system shall allow project members to update a task's
  attributes.
- **FR-4.7 Deletion:** The system shall allow a Project Admin to delete a task.
- **FR-4.8 Listing & filtering:** The system shall allow project members to list the
  tasks in a project, with support for filtering (e.g. by status or assignee), sorting,
  and pagination.

### 4.5 Comments

- **FR-5.1 Creation:** The system shall allow any member of a project to add a comment to
  a task in that project.
- **FR-5.2 Listing:** The system shall allow project members to view all comments on a
  task.
- **FR-5.3 Deletion:** The system shall allow a comment's author, or a Project Admin, to
  delete a comment.

### 4.6 Activity Log

- **FR-6.1 Recording:** The system shall record significant actions (e.g. task created,
  task status changed, member added) as activity log entries.
- **FR-6.2 Entry contents:** Each activity log entry shall capture who performed the
  action, what action was performed, the affected resource, and when it occurred.
- **FR-6.3 Scope & access:** The system shall scope activity log entries to their
  organization, and allow members to view the activity relevant to projects they can
  access.

---

## 5. Non-Functional Requirements

Non-functional requirements describe *how well* the system must behave, rather than what
it does.

- **NFR-1 Security:** Passwords shall be hashed; authentication shall use signed tokens;
  and all access shall respect tenant isolation and role-based permissions.
- **NFR-2 Documentation:** The API shall expose interactive, auto-generated documentation
  describing every endpoint.
- **NFR-3 Validation:** The system shall validate all incoming data and reject malformed
  requests with clear, structured error messages.
- **NFR-4 Testability:** Core functionality shall be covered by automated tests.
- **NFR-5 Maintainability:** The codebase shall follow a layered architecture with clear
  separation of concerns.
- **NFR-6 Consistency:** The API shall use consistent naming, predictable resource URLs,
  and appropriate HTTP status codes.