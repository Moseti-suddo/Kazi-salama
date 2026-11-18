# Kazi Salama — Project Status

## Current phase

Career profile models and initial browser UI

## Completed

- Created project folder and Python virtual environment
- Installed Django 6.1.3
- Installed psycopg 3.3.9
- Created and started PostgreSQL
- Created PostgreSQL role `mosetea`
- Created database `kazi_salama`
- Created Django project
- Configured Django to use PostgreSQL
- Set timezone to Africa/Nairobi
- Applied Django built-in migrations
- Verified Django HTTP 200
- Created private GitHub repository
- Initialized the local Git repository
- Renamed the branch to `main`
- Added the GitHub remote
- Created and registered the Django `profiles` app
- Created the `CareerProfile` model
- Created migration `profiles.0001_initial`
- Applied the CareerProfile migration to PostgreSQL
- Created PostgreSQL table `profiles_careerprofile`
- Registered `CareerProfile` in Django Admin
- Verified Django system checks pass
- Verified migration consistency
- Committed and pushed the CareerProfile checkpoint
- Created CareerProfile and Education browser forms
- Added login, logout and password URL support
- Added login template
- Added `/profile/` and `/profile/education/` routes
- Verified CareerProfile page in browser
- Verified Education page and Education creation in browser
- Added native date widgets to EducationForm
- Added migrations for Education, Experience, Project, Skill, Certification and Achievement
- Verified all profile tables exist in PostgreSQL

## Files in the local project

- `config/`
- `manage.py`
- `requirements.txt`
- `.gitignore`
- `AGENTS.md`
- `PROJECT_CONTEXT.md`
- `PROJECT_STATUS.md`
- `DECISIONS.md`
- `profiles/`

## Current blocker

None.

PostgreSQL must be active for Django database commands.

## Exact next step

Continue the profile workflow:

1. Add forms for Experience, Projects, Skills, Certifications and Achievements
2. Create repeatable list/create pages for those sections
3. Add individual confirmation and edit/remove actions
4. Add a profile wizard and review screen
5. Add SkillEvidence after the profile entry forms are stable

Verification needed before coding

• Confirm the Git remote exists:
git remote -v
• Confirm PostgreSQL is active:
systemctl is-active postgresql
• Confirm Django connects:
psql -d kazi_salama -c 'SELECT current_database(), current_user;'

## Progress checkpoint

- Commit: `e3356ac` — `Add CareerProfile model and migration`
- Created and registered the Django `profiles` app.
- Created `CareerProfile`.
- Applied migration `profiles.0001_initial`.
- PostgreSQL table `profiles_careerprofile` exists.
- Registered `CareerProfile` in Django Admin.
- Django system check passes.
- Migration consistency check passes.

## Panel explanation

The career profile is implemented as one database record per Django user. PostgreSQL stores the profile fields, while Django migrations define how the table is created and protect database consistency.
