# Kazi Salama — Project Context

## 1. Project

Kazi Salama is a final-year web application for Kenyan graduates and final-year students.

It should provide:

- A structured, reusable career profile
- Job-advert submission
- Scam-risk screening
- Skill matching and gap analysis
- Application tracking
- Later master-CV and tailored-CV generation (a limited deterministic tailored resume already exists)

The system must not:

- Submit applications automatically
- Send emails automatically
- Read a user's mailbox
- Claim that an employer is definitely fraudulent
- Invent career facts
- Use unconfirmed facts for matching or generated documents

## 2. Working Style

The user wants guided, educational help.

- Explain every step and why alternatives were rejected.
- Give exact commands or code.
- Let the user perform setup and coding.
- Do not make project changes automatically.
- Ask before automated changes.
- Wait for output when diagnosing a problem.
- Continue one focused step at a time.
- Use the project documentation as the source of truth.

During the rush before the presentation the user asked for fast, multi-step code drops. Return to one step at a time after the presentation.

## 3. MVP Workflow

1. Register and sign in.
2. Create a career profile in a guided wizard.
3. Save incomplete information as a draft.
4. Review and confirm profile entries individually.
5. Submit an advert by pasting text or providing a URL.
6. Screen the advert for scam-risk indicators.
7. Display a Low, Medium or High risk result.
8. High-risk adverts do not proceed to matching unless the user explicitly overrides.
9. Compare confirmed profile skills with advert requirements.
10. Display matched, missing and partially matched skills.
11. Display a match score, explanation and supporting profile evidence.
12. Save the advert.
13. Track the application externally.
14. Record status, deadlines, notes and next actions.

Built so far: step 1, steps 4 (for Education, Experience, Skills), 5 (pasted text only), 6, 7, 8, 9, 10 (matched and missing only), 11 (score and explanation, no supporting evidence), 12, 13, and part of 14 (status and deadline).

Not built: wizard, Save Draft, review screen, URL submission, partial matches, supporting evidence, notes form, next action, reminder date, status history.

## 4. Career Profile Sections

### Personal details

Required:

- Full name
- Email

Optional:

- Phone number
- Location
- Professional summary
- Portfolio or LinkedIn link

### Education

Required:

- Institution
- Qualification
- Field of study

Optional:

- Start date
- End date or expected completion
- Coursework or description

### Experience

Required:

- Organisation
- Role title
- Experience type
- Responsibilities and achievements

Optional:

- Location or remote status
- Start date
- End date or present
- Technologies or skills used

### Projects

Required:

- Project name
- Description
- User's role or contribution
- Technologies and tools

Optional:

- Results or achievements
- Start date
- End date or present
- Repository, demo or project URL

### Skills

Required:

- Skill name
- Category

Optional:

- Self-assessed proficiency
- Supporting profile-entry links
- Notes

Each skill should be one of:

- Claimed: entered without supporting profile evidence
- Supported: linked to education, experience or projects

Supported means the profile contains evidence, not that the user is an expert.

### Certifications and courses

Required:

- Name
- Provider
- Issue or completion date

Optional:

- Expiry date
- Verification URL
- Description or topics

### Achievements and awards

Required:

- Title
- Issuing organisation
- Date

Optional:

- Description
- Evidence URL

## 5. Profile Behavior

- Use a multi-step wizard.
- Include Next, Back and Save Draft controls.
- Allow incomplete drafts.
- Use a final Review and Confirm screen.
- Confirm entries individually.
- Allow edit, remove and confirm actions.
- Exclude unconfirmed entries from matching.
- Keep the main profile separate from tailored application data.

## 6. Scam and Matching Behavior

The MVP should use a hybrid approach:

- LLM: structured extraction of skills and warning candidates (not built yet)
- Python rules: scam-risk calculation (built, `profiles/scam.py`)
- Python scoring: skill match and missing skill calculation (built, `profiles/matching.py`)

The LLM must not:

- Make the final scam-risk decision
- Make the final fit decision
- Receive tools or database access
- Return free-form output that is directly accepted as a result

Scam output:

- Low, Medium or High
- Detected indicators
- Plain-language explanation
- Recommendation
- Disclaimer that this is not proof of fraud

Match output:

- Matched skills
- Missing skills
- Partially matched skills (not built)
- Match score
- Calculation explanation
- Supporting profile evidence (not built)

Current thresholds: Low below 30, Medium 30 to 59, High 60 or more. Weights are starting values, not validated against real adverts.

## 7. Application Tracker

Statuses:

- Saved
- Preparing application
- Submitted externally
- Interview
- Offer received
- Rejected
- Withdrawn

Store:

- Deadline
- Status history with timestamps
- Notes
- Next action
- Reminder date

The system never marks an application as submitted unless the user confirms it.

Currently stored on the Advert record: status, deadline, notes field. The rest is not built.

## 8. Technology Decisions

- Language: Python 3.14 (3.14.10 seen on the development machine; earlier notes said 3.14.8)
- Web framework: Django 6.1.3 (pinned in requirements.txt; the venv must be active, because system Django 5.2.17 was used by mistake once)
- Database: PostgreSQL 18.6
- PostgreSQL Python driver: psycopg 3.3.9
- Frontend: Django templates with plain CSS in `templates/base.html`
- Styling: Tailwind CSS, to be added later
- Interactivity: HTMX, to be added later
- Node.js: 24.21.0
- npm: 12.2.0
- Git: 2.53.0
- Project timezone: Africa/Nairobi
- Architecture: Django modular monolith

Django was selected because it provides authentication, forms, validation, templates and ORM support in one framework. It avoids the extra complexity of separate React and API projects during the MVP.

PostgreSQL was selected for structured relationships, foreign keys and application-history records.

Tailwind and HTMX will be added after core Django structure is working.

## 9. Current Environment

Project folder: `/home/mosetea/Projects/kazi-salama`

Virtual environment: `/home/mosetea/Projects/kazi-salama/.venv`

Activate it with:

```bash
cd ~/Projects/kazi-salama
source .venv/bin/activate
```

PostgreSQL database:

- Database: `kazi_salama`
- Local role: `mosetea`
- Authentication: local Unix socket

Running the tests may need the role to create a test database:

```bash
sudo -u postgres psql -c "ALTER ROLE mosetea CREATEDB;"
```

Django files:

- `config/settings.py`
- `config/urls.py`
- `config/asgi.py`
- `config/wsgi.py`
- `manage.py`
- `requirements.txt`
- `.gitignore`

Accounts app files:

- `accounts/forms.py` (`RegisterForm`), `views.py` (`register`), `urls.py`, `tests.py` (10 tests)
- `templates/registration/register.html`

Profiles app files:

- `profiles/models.py`, `forms.py`, `views.py`, `urls.py`, `admin.py`
- `profiles/scam.py` (scam rules)
- `profiles/matching.py` (skill matching)
- `profiles/tests.py` (5 tests)
- `profiles/migrations/0001` to `0007`

Templates (Django searches both folders: `DIRS` and `APP_DIRS`):

- `templates/base.html`
- `templates/registration/login.html`
- `templates/profiles/dashboard.html`, `education_list.html`, `skill_list.html`, `experience_list.html`
- `templates/profiles/advert_list.html`, `advert_detail.html`, `resume.html`
- `profiles/templates/profiles/profile_edit.html` (the only copy; used by `/profile/`)

Django settings currently configure:

- PostgreSQL backend
- Database name `kazi_salama`
- Local user `mosetea`
- Timezone `Africa/Nairobi`
- `LOGIN_REDIRECT_URL = "profile_edit"`, `LOGOUT_REDIRECT_URL = "login"`

Django dependencies in `requirements.txt`:

```
Django==6.1.3
psycopg[binary]==3.3.9
```

## 10. Setup Completed

- Created project folder
- Created `.venv`
- Installed Django
- Installed psycopg
- Started PostgreSQL
- Created PostgreSQL role `mosetea`
- Created database `kazi_salama`
- Created Django project
- Refreshed PostgreSQL collation versions
- Ran Django system check successfully
- Applied Django built-in migrations successfully
- Added requirements and .gitignore
- Confirmed Django returned HTTP 200 locally
- Configured Django to use PostgreSQL
- Created private GitHub repository: https://github.com/Moseti-suddo/Kazi-salama.git
- Created and registered the Django `profiles` app
- Created the `CareerProfile` model
- Applied migration `profiles.0001_initial`
- Verified PostgreSQL table `profiles_careerprofile`
- Registered `CareerProfile` in Django Admin
- Committed checkpoint `e3356ac`
- Pushed the checkpoint to GitHub
- Created and applied migrations for all basic profile models
- Built login, profile, education, skills and experience pages with confirm toggles
- Built the shared layout and dashboard
- Built the advert model, scam rules, matching, advert pages and status tracking
- Built the tailored resume page

## 11. Current Position

The Django environment is working and the core demo flow runs: confirm skills, paste an advert, see the scam-risk result and indicators, see the skill match against confirmed skills only, update the application status, and generate a tailored resume.

CareerProfile contains:

- One-to-one ownership by Django's built-in User
- Full name
- Phone number
- Location
- Professional summary
- Portfolio URL
- Whole-profile confirmation state
- Creation and update timestamps

Email is not a CareerProfile field. The resume reads the Django user's email.

Database tables:

- `profiles_careerprofile`
- `profiles_education`
- `profiles_experience`
- `profiles_project`
- `profiles_skill`
- `profiles_certification`
- `profiles_achievement`
- `profiles_advert`

Working browser routes:

- `/accounts/register/` — create an account (signed in automatically, then `/profile/`)
- `/accounts/login/` — sign in
- `/` — dashboard
- `/profile/` — create and edit CareerProfile
- `/profile/education/` — list, add and confirm education
- `/profile/skills/` — list, add and confirm skills
- `/profile/experience/` — list, add and confirm experience
- `/adverts/` — list adverts and screen a new one
- `/adverts/<id>/` — risk result, match result, status update, resume link, delete
- `/adverts/<id>/override/` — POST, match a High-risk advert anyway
- `/adverts/<id>/status/` — POST, update application status
- `/adverts/<id>/delete/` — POST, delete advert
- `/adverts/<id>/resume/` — tailored resume (only after matching)

Provided but not yet verified in the browser: skill add, experience page, delete advert, sidebar restyle and dark mode, resume page.


The next implementation step is in PROJECT_STATUS.md.

## 12. Deferred Features

Do not begin these features until the core MVP works:

- GitHub evidence
- Referees
- CV/PDF upload
- CV text extraction
- Master CV
- AI-written or LLM-drafted CV content
- Cover-letter generation
- Application email drafting
- Automated job collection
- Daily job agent
- LinkedIn integration
- Mailbox integration
- Automatic job submission
- WhatsApp integration
- Scikit-learn models
- Advanced LLM chat or drafting
- External cloud deployment

The deterministic tailored resume (confirmed entries only, no AI) was built early for the presentation. See DECISIONS.md.

## 13. Documentation Files

- Chapters 4 and 5 PDF: `/home/mosetea/Downloads/Kazi_Salama_Chapters_4_5.pdf`
- Editable Chapters 4 and 5 Word document: `/home/mosetea/Downloads/Kazi_Salama_Chapters_4_5.docx`
- Chapters 4 and 5 HTML source: `/home/mosetea/Downloads/Kazi_Salama_Chapters_4_5.html`
- Task 2 profile PDF: `/home/mosetea/Downloads/Kazi_Salama_Task_2_Career_Profile.pdf`
- Supplied project guidelines: `/home/mosetea/Downloads/Undergraduate Project Paper Guidelines March 20172.pdf`

## 14. PostgreSQL Troubleshooting

If Django reports that PostgreSQL socket `/var/run/postgresql/.s.PGSQL.5432` is unavailable:

```bash
sudo systemctl start postgresql
systemctl is-active postgresql
psql -d kazi_salama -c 'SELECT current_database(), current_user;'
```

## 15. Instructions for the Next AI

Before answering or changing files:

1. Read this entire document.
2. Preserve the established MVP scope and technology stack.
3. Follow the user's request to perform setup and coding themselves.
4. Explain concepts and choices clearly.
5. Give commands or code one step at a time.
6. Do not make changes automatically.
7. Ask before using tools or automation.
8. Update `PROJECT_STATUS.md` after meaningful progress.
9. Never store passwords, API keys or personal data in project documentation.
10. Do not claim a feature works until the user has shown its output. Check the "not yet verified" list in PROJECT_STATUS.md first.
11. Check that the virtual environment is active before any Django command.
