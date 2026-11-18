# Agent Instructions

## User preference

The user wants to perform setup and coding themselves. Agents must:

- Explain every step clearly.
- Explain why each choice was made and what alternative was rejected.
- Give exact commands or code for the user to run.
- Wait for the user's output before continuing after an error.
- Ask before making or automating project changes.
- Continue one step at a time.
- Not claim that a command was successful until its output is verified.

## Required files

Before working, read:

1. `AGENTS.md`
2. `PROJECT_CONTEXT.md`
3. `DECISIONS.md`
4. `PROJECT_STATUS.md`

## Project rules

- Preserve the Django modular-monolith architecture.
- Preserve PostgreSQL as the database.
- Preserve Django templates for the MVP.
- Use Tailwind CSS and HTMX only when the relevant frontend step is reached.
- Preserve the profile-first implementation order.
- Do not begin GitHub evidence, CV extraction, master-CV drafting, ad collection, or the daily agent before the core profile workflow works.
- Do not submit applications or send emails.
- Treat scam results as warning indicators, not proof of fraud.
- Do not use unconfirmed profile facts for matching.
- Do not store passwords, API keys, personal data or database credentials in this repository.

## After meaningful work

Update `PROJECT_STATUS.md` with:

- Work completed
- Files changed
- Commands or tests that succeeded
- Errors and unresolved blockers
- The exact next step
