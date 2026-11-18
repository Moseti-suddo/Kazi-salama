# Kazi Salama — Project Context

1. Project

Kazi Salama is a final-year web application for Kenyan graduates and final-year students.

It should provide:

• A structured, reusable career profile
• Job-advert submission
• Scam-risk screening
• Skill matching and gap analysis
• Application tracking
• Later master-CV and tailored-CV generation

The system must not:

• Submit applications automatically
• Send emails automatically
• Read a user's mailbox
• Claim that an employer is definitely fraudulent
• Invent career facts
• Use unconfirmed facts for matching or generated documents

2. Working Style

The user wants guided, educational help.

• Explain every step and why alternatives were rejected.
• Give exact commands or code.
• Let the user perform setup and coding.
• Do not make project changes automatically.
• Ask before automated changes.
• Wait for output when diagnosing a problem.
• Continue one focused step at a time.
• Use the project documentation as the source of truth.

3. MVP Workflow

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

4. Career Profile Sections

Personal details

Required:

• Full name
• Email

Optional:

• Phone number
• Location
• Professional summary
• Portfolio or LinkedIn link

Education

Required:

• Institution
• Qualification
• Field of study

Optional:

• Start date
• End date or expected completion
• Coursework or description

Experience

Required:

• Organisation
• Role title
• Experience type
• Responsibilities and achievements

Optional:

• Location or remote status
• Start date
• End date or present
• Technologies or skills used

Projects

Required:

• Project name
• Description
• User's role or contribution
• Technologies and tools

Optional:

• Results or achievements
• Start date
• End date or present
• Repository, demo or project URL

Skills

Required:

• Skill name
• Category

Optional:

• Self-assessed proficiency
• Supporting profile-entry links
• Notes

Each skill should be one of:

• Claimed: entered without supporting profile evidence
• Supported: linked to education, experience or projects

Supported means the profile contains evidence, not that the user is an expert.

Certifications and courses

Required:

• Name
• Provider
• Issue or completion date

Optional:

• Expiry date
• Verification URL
• Description or topics

Achievements and awards

Required:

• Title
• Issuing organisation
• Date

Optional:

• Description
• Evidence URL

5. Profile Behavior

• Use a multi-step wizard.
• Include Next, Back and Save Draft controls.
• Allow incomplete drafts.
• Use a final Review and Confirm screen.
• Confirm entries individually.
• Allow edit, remove and confirm actions.
• Exclude unconfirmed entries from matching.
• Keep the main profile separate from tailored application data.

6. Scam and Matching Behavior

The MVP should use a hybrid approach:

• LLM: structured extraction of skills and warning candidates
• Python rules: scam-risk calculation
• Python scoring: skill match, partial match and missing skill calculation

The LLM must not:

• Make the final scam-risk decision
• Make the final fit decision
• Receive tools or database access
• Return free-form output that is directly accepted as a result

Scam output:

• Low, Medium or High
• Detected indicators
• Plain-language explanation
• Recommendation
• Disclaimer that this is not proof of fraud

Match output:

• Matched skills
• Missing skills
• Partially matched skills
• Match score
• Calculation explanation
• Supporting profile evidence

7. Application Tracker

Statuses:

• Saved
• Preparing application
• Submitted externally
• Interview
• Offer received
• Rejected
• Withdrawn

Store:

• Deadline
• Status history with timestamps
• Notes
• Next action
• Reminder date

The system never marks an application as submitted unless the user confirms it.

8. Technology Decisions

• Language: Python 3.14.8
• Web framework: Django 6.1.3
• Database: PostgreSQL 18.6
• PostgreSQL Python driver: psycopg 3.3.9
• Frontend: Django templates
• Styling: Tailwind CSS, to be added later
• Interactivity: HTMX, to be added later
• Node.js: 24.21.0
• npm: 12.2.0
• Git: 2.53.0
• Project timezone: Africa/Nairobi
• Architecture: Django modular monolith

Django was selected because it provides authentication, forms, validation, templates and ORM support in one framework. It avoids the extra complexity of separate React and API projects during the MVP.

PostgreSQL was selected for structured relationships, foreign keys and application-history records.

Tailwind and HTMX will be added after core Django structure is working.

9. Current Environment

Project folder:
 /home/mosetea/Projects/kazi-salama 

Virtual environment:
 /home/mosetea/Projects/kazi-salama/.venv 

Activate it with:

cd ~/Projects/kazi-salama
source .venv/bin/activate

PostgreSQL database:

• Database:  kazi_salama 
• Local role:  mosetea 
• Authentication: local Unix socket

Current Django files:

•  config/settings.py 
•  config/urls.py 
•  config/asgi.py 
•  config/wsgi.py 
•  manage.py 
•  requirements.txt 
•  .gitignore 

Django settings currently configure:

• PostgreSQL backend
• Database name  kazi_salama 
• Local user  mosetea 
• Timezone  Africa/Nairobi 

Django dependencies in  requirements.txt :

Django==6.1.3
psycopg[binary]==3.3.9

10. Setup Completed

• Created project folder
• Created  .venv 
• Installed Django
• Installed psycopg
• Started PostgreSQL
• Created PostgreSQL role  mosetea 
• Created database  kazi_salama 
• Created Django project
• Refreshed PostgreSQL collation versions
• Ran Django system check successfully
• Applied Django built-in migrations successfully
• Added requirements and .gitignore
• Confirmed Django returned HTTP 200 locally
• Configured Django to use PostgreSQL
• Created private GitHub repository:
 https://github.com/Moseti-suddo/Kazi-salama.git 
• Created and registered the Django `profiles` app
• Created the `CareerProfile` model
• Applied migration `profiles.0001_initial`
• Verified PostgreSQL table `profiles_careerprofile`
• Registered `CareerProfile` in Django Admin
• Committed checkpoint `e3356ac`
• Pushed the checkpoint to GitHub

11. Current Position

The Django environment is initialized and the first custom application, `profiles`, is registered and working.

CareerProfile currently contains:

• One-to-one ownership by Django's built-in User
• Full name
• Phone number
• Location
• Professional summary
• Portfolio URL
• Whole-profile confirmation state
• Creation and update timestamps

The `profiles_careerprofile` PostgreSQL table exists.

The next implementation step is to create the remaining profile models:

1. Education
2. Experience
3. Project
4. Skill
5. Certification
6. Achievement

SkillEvidence will be added after these basic models work.

12. Deferred Features

Do not begin these features until the core MVP works:

• GitHub evidence
• Referees
• CV/PDF upload
• CV text extraction
• Master CV
• Tailored CV
• Cover-letter generation
• Application email drafting
• Automated job collection
• Daily job agent
• LinkedIn integration
• Mailbox integration
• Automatic job submission
• WhatsApp integration
• Scikit-learn models
• Advanced LLM chat or drafting
• External cloud deployment

13. Documentation Files

• Chapters 4 and 5 PDF:
 /home/mosetea/Downloads/Kazi_Salama_Chapters_4_5.pdf 
• Editable Chapters 4 and 5 Word document:
 /home/mosetea/Downloads/Kazi_Salama_Chapters_4_5.docx 
• Chapters 4 and 5 HTML source:
 /home/mosetea/Downloads/Kazi_Salama_Chapters_4_5.html 
• Task 2 profile PDF:
 /home/mosetea/Downloads/Kazi_Salama_Task_2_Career_Profile.pdf 
• Supplied project guidelines:
 /home/mosetea/Downloads/Undergraduate Project Paper Guidelines March 20172.pdf 

14. PostgreSQL Troubleshooting

If Django reports that PostgreSQL socket  /var/run/postgresql/.s.PGSQL.5432  is unavailable:

sudo systemctl start postgresql
systemctl is-active postgresql
psql -d kazi_salama -c 'SELECT current_database(), current_user;'

15. Instructions for the Next AI

Before answering or changing files:

1. Read this entire document.
2. Preserve the established MVP scope and technology stack.
3. Follow the user's request to perform setup and coding themselves.
4. Explain concepts and choices clearly.
5. Give commands or code one step at a time.
6. Do not make changes automatically.
7. Ask before using tools or automation.
8. Update  PROJECT_STATUS.md  after meaningful progress.
9. Never store passwords, API keys or personal data in project documentation.
