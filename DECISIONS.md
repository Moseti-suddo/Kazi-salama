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

Email is required at registration and must be unique, ignoring case. Uniqueness is enforced in forms (`clean_unique_email()` in `accounts/forms.py`, used by `RegisterForm` and `AccountEmailForm`), not the database, because the built-in `User.email` column is not unique. Users created through Django Admin bypass this check.

New users are signed in immediately after registering. There is no email verification because the MVP sends no email.

## Profile creation

Profile information will be entered through forms and a guided wizard. The wizard is not built yet; entry pages with add and confirm exist for Education, Experience, Projects and Skills, and Education, Experience and Projects also have edit and remove.

CV upload will come later. It may extract suggested details, but it must not silently confirm or add them to the profile.

## Personal details (Feature 2, 2026-11-23)

Email stays on Django's `User` and is edited on the profile page through `AccountEmailForm`, rendered with `CareerProfileForm` in one form with one Save button. Both forms must be valid before either is saved, and they are saved in one transaction. An `email` field on `CareerProfile` was rejected because two copies would drift apart, and the resume and the duplicate-email rule already use `User.email`.

Full name is required by the form. The database can still hold a blank name, because `get_profile()` creates profiles lazily with `user.get_full_name()`, which is empty after registration. Lazy creation is kept because it also covers Admin-created and older users. A `post_save` signal and creating the profile only at registration were rejected.

Phone number gets a light form check (digits, spaces, `+`, `-`, brackets, at least 7 digits). `django-phonenumber-field` was rejected as an extra dependency for an optional field.

Labels and help text are set in the form, not the model, so no migration was needed.

Personal details have no Remove action. Deleting `CareerProfile` would cascade and delete every profile entry and advert. Users can clear the optional fields instead.

## Education (Feature 3, 2026-11-23)

No model fields were added; the existing fields match the spec.

"Expected completion" is a future `end_date`, labelled "End date or expected completion". The `is_expected` property (end date after today in Africa/Nairobi) is computed when the page is shown. An `is_expected` or `is_current` checkbox was rejected because it needs a migration and allows contradictions such as a ticked box with a past date.

An end date before the start date is rejected in `EducationForm.clean()`, with the error on `end_date`. Equal dates and blank dates are allowed. A database `CheckConstraint` was rejected because it needs a migration that fails if any existing row breaks the rule. `Model.clean()` was rejected to keep validation in forms, like the phone and email rules. Since Feature 4 the rule lives in the shared `validate_date_range()` helper (see Experience below).

Ordering is explicit: blank end dates first (usually still studying), then newest end date, then start date, then `-created_at` so the order never depends on chance. This needed migration 0008, which runs no SQL. The ordering stays in `Meta` because the dashboard and resume rely on it too.

Edit is a separate page (`/profile/education/<pk>/edit/`). Editing inside the list page was rejected because it mixes two forms in one view, and HTMX is deferred. Remove is POST only with a browser confirm prompt, the same as advert delete; a separate confirmation page was rejected as an extra view and template. Edit, remove and confirm all look up entries with `profile__user=request.user`, so another user's entry returns 404.

Date inputs use `format="%Y-%m-%d"`, because browser date inputs only accept that format. Without it a saved date could show as blank on the edit page and be wiped on save.

## Experience (Feature 4, 2026-11-25)

No model fields were added; the existing fields match the spec. "End date or present" is the existing `is_current` checkbox, labelled "I currently work here". Unlike Education, a checkbox fits here because a current job has no known end date to compare with today.

The date rules live in one function, `validate_date_range(form, cleaned_data, current_field=None)` in `profiles/forms.py`, called from `EducationForm.clean()` and `ExperienceForm.clean()` (and `ProjectForm.clean()` since Feature 5). It rejects an end date before the start date and, when `current_field` is given, a ticked "current" box together with an end date. Both errors go on `end_date`. A mixin class was rejected because its `super()` ordering is harder to follow and gains nothing for three forms. Silently clearing the end date when "current" is ticked was rejected because it discards what the user typed without telling them.

`technologies` stays free text. Linking skills to the entries that support them is Feature 6.

The experience types stay Employment, Internship and Volunteer. Adding "Attachment" (Kenyan industrial attachment) was considered and left for later; it needs only a `choices` migration.

Ordering is in `Meta`: current roles first, then newest end date (blanks first), then newest start date, then `-created_at`. This needed migration 0009, which runs no SQL. The list view and the resume no longer call `.order_by("-start_date")`; the resume's relevance sort is stable, so equally relevant entries keep this order.

Edit, remove, confirm and messages follow the Education pattern (Feature 3), including resetting confirmation when a saved edit changes a value.

Required fields also get the browser's own "Please fill out this field." bubble, because Django renders a `required` attribute. In Firefox the bubble stays fixed on screen while scrolling; this is browser behaviour, not page CSS. The bubble is kept on every form for instant feedback, with the server-side check as the real safeguard. Adding `novalidate` to forms was rejected for now; if wanted, it should be applied to all forms at once as a separate task.

## Projects (Feature 5, 2026-11-25)

No model fields were added; the existing fields match the spec. "End date or present" is the existing `is_current` checkbox, labelled "I'm still working on this", for the same reason as Experience.

`ProjectForm.clean()` is the third user of `validate_date_range(..., current_field="is_current")`. Writing a separate date check for Projects was rejected so all three forms follow one rule.

The URL field gets no custom `clean_url()`. Django 6's form `URLField` already adds `https://` when the scheme is missing, as on the profile page; a test covers it. On the list page the link opens in a new tab with `rel="noopener noreferrer"`, so the linked site cannot reach the Kazi Salama tab through `window.opener`.

Ordering, edit, remove, confirm and messages follow Experience (Feature 4): current projects first, then newest end date, then newest start date, then `-created_at` (migration 0010, no SQL), and a saved change resets confirmation.

The resume still shows only name, role, description and technologies for projects. Adding outcomes, URL and dates was left for Feature 12 to keep this feature focused.

## Confirmation

Every profile entry must be reviewed and confirmed individually. Personal details count as one entry, confirmed with the `profile_confirmed` flag (toggled at `/profile/confirm/`). Personal details can only be confirmed once full name and email are filled in.

A saved edit that changes any value makes the entry unconfirmed again, so "confirmed" always means the user reviewed the current content. Saving without changes keeps it confirmed. This applies to personal details now and to every entry type when its edit view is added (Features 3–7). Keeping confirmation after an edit was rejected because a wrong change would still count as confirmed.

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
