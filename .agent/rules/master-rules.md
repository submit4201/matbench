---
trigger: manual
---

master rules

1. build in python 
    1-A: unless we are building a gui or front end [then use typescript, javascript, or react, or some other framework that would be fun to try] ( like ive  never used django and had it look like a modern app)

2. Logging - Must be logged to a file and the console and the file should be in a .log directory in the root of the project.
    2-A: in the .log directory there should be if more then one type of logging happening they should be in their own folder 
    2-B: then each folder should have logs named by date and time with a descriptor of the type of log it is eg GameMaster-MM-DD-YYYY--HH.log[HH could be hour or run number]
    2-C: the logs should be rotated every couple of hours and the logs should be compressed into a .zip file
    2-D: the logs should be compressed into a .zip file at the end of the day

3. Testing - Must be tested with pytest and the tests should be in a .test directory in the root of the project.
    3-A: in the .test directory there should be a directory structure that matches the directory structure of the project
    3-B: all tests should be in a file named test_*.py 
    3-C: all tests should log they're results to the console and to a file
    3-D: those logs should be housed with the logging system but kept with the test files
    3-E: those logs should follow the same rotation and compression system as the logging system

4. Comments - should be consistent and easy to read and parse 
    4-A: use docstrings for functions and classes
    4-B: use comments for logic and flow
    4-C: use comments for debugging
    4-D: use comments for TODOs, FIXMEs, and HACKS, QUESTIONS, and NOTES
    4-E: comments with [ ] should be parsed and logged to a file for review and completion and conversation
    4-F: a ! should be used to mark important things 
    4-G: a ? should be used to mark questions
    4-H: a * should be used to mark notes
    4-I: we should parse the comments ever couple of hours and log them to .todo directory with a timestamp and a discriptor 
    4-J: we'll zip the completed comments and move them to a .done directory in the .todo directory

5. Architecture - needs to stay consistent, and be easy to understand and navigate
    5-A: use a consistent naming convention for files and directories
    5-B: use a consistent naming convention for classes and functions
    5-C: use a consistent naming convention for variables and constants
    5-D: use a consistent naming convention for modules and packages
    5-E: use a consistent naming convention for files and directories
    5-F respect separation of concerns
    5-G: Frontend should be for User interaction 
    5-H: Backend should be for Business logic, api, Database, and Logic 
    5-I: Middleware for Validations, authentication, logging, Error handling, security and other cross-cutting concerns
    5-J: models should be that of schemas, pydantic models, and database models

6. Create README.md for explanations of directories and expectations for those directories
7. always create TASK artifacts for your sprints make them as granular as possible
8. if in question ask 

9. NEVER MERGE _ OR PUSH YOUR WORK TO A MAIN OR MASTER BRANCH you may create a request and you can make a new branch for your work but any new mergeing to main or master requires a code review
<|-STOP AND CONSIDER HAVE YOU COMMITED - PUSHED - TAGGED - BRANCHED - MERGED - YOUR WORK TO GITHUB? IF NOT DO IT NOW|>
. The Golden Rule: "Type / ID / Description"
The most effective structure uses forward slashes. Many Git tools (like SourceTree, GitKraken, or GitHub Desktop) will actually group these into "folders" visually, which helps immensely with organization.

Structure: category/ticket-ID/short-description

Category: What kind of work is this? (See list below)

Ticket ID: (Optional but recommended) The issue number from Jira, Trello, or GitHub Issues. This links the code to your project management tool.

Description: 2-3 words explaining what the branch does.

Examples:

feature/JIRA-42/add-dark-mode

bugfix/issue-102/fix-login-crash

hotfix/urgent-db-patch

2. Standard Branch Categories
Using consistent prefixes helps you identify the urgency and risk of a branch at a glance.

feature/: For new functionality (e.g., feature/user-profile).

bugfix/: For fixing a bug in the code that is not currently in production (e.g., bugfix/calendar-glitch).

hotfix/: For urgent fixes that need to go directly to production to patch a live issue (e.g., hotfix/security-patch).

release/: For preparing a new version release (e.g., release/v1.2.0).

chore/ or maintenance/: For code maintenance that doesn't change functionality, like updating libraries or cleaning comments (e.g., chore/update-react).

experiment/ or poc/: For proof-of-concept code that might not ever be merged.

3. How to avoid overlooking Merged vs. Unmerged branches
The user specifically asked about tracking what needs to be merged versus what is already done. Naming conventions help, but workflow is the real solution here.

Delete After Merge: The best convention for a branch that "has been merged" is for it to not exist. Configure your repository (GitHub/GitLab) to "Automatically delete head branches" after a Pull Request is merged. If a branch exists, it means work is still active.

Use Pull Requests (PRs) as status indicators: Do not use branch names to indicate status (e.g., avoid feature/login-ready-for-review). Instead, open a Draft PR.

No PR: Work in progress.

Open PR: Ready for review/merge.

Closed/Merged PR: Done (Branch should be deleted).

4. General Formatting Rules
To avoid technical errors in terminal commands:

Use lowercase only: Feature/New-Thing is harder to type than feature/new-thing.

Use hyphens, not underscores: Hyphens (-) are generally easier to read and type than underscores (_).

No spaces: Never use spaces in branch names.. The Golden Rule: "Type / ID / Description"
The most effective structure uses forward slashes. Many Git tools (like SourceTree, GitKraken, or GitHub Desktop) will actually group these into "folders" visually, which helps immensely with organization.

Structure: category/ticket-ID/short-description

Category: What kind of work is this? (See list below)

Ticket ID: (Optional but recommended) The issue number from Jira, Trello, or GitHub Issues. This links the code to your project management tool.

Description: 2-3 words explaining what the branch does.

Examples:

feature/JIRA-42/add-dark-mode

bugfix/issue-102/fix-login-crash

hotfix/urgent-db-patch

2. Standard Branch Categories
Using consistent prefixes helps you identify the urgency and risk of a branch at a glance.

feature/: For new functionality (e.g., feature/user-profile).

bugfix/: For fixing a bug in the code that is not currently in production (e.g., bugfix/calendar-glitch).

hotfix/: For urgent fixes that need to go directly to production to patch a live issue (e.g., hotfix/security-patch).

release/: For preparing a new version release (e.g., release/v1.2.0).

chore/ or maintenance/: For code maintenance that doesn't change functionality, like updating libraries or cleaning comments (e.g., chore/update-react).

experiment/ or poc/: For proof-of-concept code that might not ever be merged.

3. How to avoid overlooking Merged vs. Unmerged branches
The user specifically asked about tracking what needs to be merged versus what is already done. Naming conventions help, but workflow is the real solution here.

Delete After Merge: The best convention for a branch that "has been merged" is for it to not exist. Configure your repository (GitHub/GitLab) to "Automatically delete head branches" after a Pull Request is merged. If a branch exists, it means work is still active.

Use Pull Requests (PRs) as status indicators: Do not use branch names to indicate status (e.g., avoid feature/login-ready-for-review). Instead, open a Draft PR.

No PR: Work in progress.

Open PR: Ready for review/merge.

Closed/Merged PR: Done (Branch should be deleted).

4. General Formatting Rules
To avoid technical errors in terminal commands:

Use lowercase only: Feature/New-Thing is harder to type than feature/new-thing.

Use hyphens, not underscores: Hyphens (-) are generally easier to read and type than underscores (_).

No spaces: Never use spaces in branch names.