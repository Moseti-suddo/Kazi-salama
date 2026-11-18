
# Kazi Salama — Decisions

## Architecture

Django modular monolith with PostgreSQL.

Django was chosen instead of FastAPI + React because this MVP needs authentication, server-rendered forms, validation and a relational database more than a separate frontend application.

## Database

PostgreSQL is the development and planned application database.

SQLite was rejected for the MVP because PostgreSQL better matches the project description and the final relational design.

## Frontend

Django templates are the initial frontend.

Tailwind CSS and HTMX will be added later:
- Tailwind CSS: consistent styling and responsive layouts
- HTMX: small server-driven interactions without a separate React application

React was deferred because it creates two applications and additional API, build and deployment complexity.

## Profile creation

Profile information will be entered through forms and a guided wizard.

CV upload will come later. It may extract suggested details, but it must not silently confirm or add them to the profile.

## Confirmation

Every profile entry must be reviewed and confirmed individually.

Unconfirmed facts are excluded from matching and future document generation.

## Scam screening

The MVP uses a hybrid approach:
- LLM: extract structured candidate skills and warning signals
- Python rules: calculate scam risk
- Python scoring: calculate skill match and gaps

LLM-only decisions were rejected because they are less explainable and less testable.

## Risk result

Risk levels:
- Low
- Medium
- High

High-risk adverts are not matched unless the user explicitly overrides the warning.

The interface must state that risk output is not proof of fraud.

## Application tracking

Statuses:
- Saved
- Preparing application
- Submitted externally
- Interview
- Offer received
- Rejected
- Withdrawn

The system will never mark Submitted automatically.

## Deferred scope

Deferred until the core workflow works:
- GitHub evidence
- Referees
- CV/PDF parsing
- Master CV
- Tailored CV
- Cover letters
- Job collection
- Daily agent
- Email or application automation
- LinkedIn or mailbox integration
- Machine-learning models
- Advanced LLM drafting
