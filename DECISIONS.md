# Kazi Salama — Decisions

## Architecture

Django modular monolith with PostgreSQL.

Django was chosen instead of FastAPI + React because this MVP needs authentication, server-rendered forms, validation and a relational database more than a separate frontend application.

## Database

PostgreSQL is the development and planned application database.

SQLite was rejected for the MVP because PostgreSQL better matches the project description and the final relational design.

## Frontend

Django templates are the initial frontend, with plain CSS in `base.html` (cream/sage/green/coral palette, Instrument Serif and Inter, dark mode toggle).

Tailwind CSS and HTMX are still deferred:
- Tailwind CSS: consistent styling and responsive layouts
- HTMX: small server-driven interactions without a separate React application

Plain CSS was used for the demo because it needed no build step. Tailwind remains a later option.

React was deferred because it creates two applications and additional API, build and deployment complexity.

## Accounts

Registration lives in a separate `accounts` app, not in `profiles`. Identity and career data are different concerns in the modular monolith.

Django's built-in `User` and `UserCreationForm` are used. A custom user model was rejected because replacing `User` this late is a large, risky migration. `django-allauth` was rejected as an unnecessary dependency.

Email is required at registration and must be unique, ignoring case. Uniqueness is enforced in `RegisterForm`, not the database, because the built-in `User.email` column is not unique. Users created through Django Admin bypass this check.

New users are signed in immediately after registering. There is no email verification because the MVP sends no email.

## Profile creation

Profile information will be entered through forms and a guided wizard. The wizard is not built yet; entry pages with add and confirm exist for Education, Experience and Skills.

CV upload will come later. It may extract suggested details, but it must not silently confirm or add them to the profile.

## Confirmation

Every profile entry must be reviewed and confirmed individually.

Unconfirmed facts are excluded from matching and generated documents. This is enforced in the matching view and the resume view, which both filter on `is_confirmed=True`.

## Scam screening

The MVP uses a hybrid approach by design:
- LLM: extract structured candidate skills and warning signals (not built yet)
- Python rules: calculate scam risk (built)
- Python scoring: calculate skill match and gaps (built)

LLM-only decisions were rejected because they are less explainable and less testable.

Current implementation: eight weighted regular-expression rules in `profiles/scam.py` (fees, sensitive details, WhatsApp/Telegram-only contact, free email contact, guaranteed job, unrealistic pay, overseas recruitment pressure, urgency). Score is capped at 100.

Rules were chosen over a model because each result can be traced to the rule that fired and each rule can be unit tested.

Weights and thresholds are starting values and have not been validated against real adverts.

## Risk result

Risk levels:
- Low: score below 30
- Medium: score 30 to 59
- High: score 60 or more

High-risk adverts are not matched unless the user explicitly overrides the warning with a button on the advert page.

The interface states that risk output is not proof of fraud. Low risk is not described as safe.

## Skill matching

Matching compares the skills an advert mentions with the user's confirmed skills only.

The advert's required skills are found by searching for a fixed `KNOWN_SKILLS` list plus the user's own confirmed skill names. Score is matched divided by required, rounded.

Limitation: skills outside the fixed list are missed. LLM extraction is the planned fix. Partial matches are not implemented.

## Application tracking

Statuses:
- Saved
- Preparing application
- Submitted externally
- Interview
- Offer received
- Rejected
- Withdrawn

The user changes the status manually. The system never marks Submitted automatically and never submits applications or sends email.

Currently stored: status, deadline, notes field (no form yet). Status history with timestamps, next action and reminder date are not built yet.

## Tailored resume (decision changed)

Earlier versions of this document deferred all CV generation. A limited version was built for the presentation:
- Generated from confirmed entries only
- No AI and no invented content
- Skills, experience and projects that match the advert are ordered first
- Only available once matching has run, so a High-risk advert needs the override first
- Printed or saved as PDF from the browser

The master CV, AI-written content, CV upload and cover letters remain deferred.

## Deferred scope

Deferred until the core workflow works:
- GitHub evidence
- Referees
- CV/PDF parsing
- Master CV
- AI-written CV content
- Cover letters
- Job collection
- Daily agent
- Email or application automation
- LinkedIn or mailbox integration
- Machine-learning models
- Advanced LLM drafting
