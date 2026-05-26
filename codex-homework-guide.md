---
name: easyhpc-homework
description: "End-to-end EasyHPC homework workflow: first-use private .env setup, authenticated homework list/download/upload, coding lab implementation, experiment verification, Chinese XeLaTeX reports, theory-answer PDFs, packaging, submission, and server-copy verification. Use for EasyHPC, easyhpc.net, course homework, Pthreads/OpenMP/MPI labs, homework reports, zip packaging, upload, or submission verification."
---

# EasyHPC Homework

Use this skill to complete EasyHPC homework end to end. The workflow covers protected material download, requirement extraction,
programming labs, theory assignments, Chinese XeLaTeX reports, zip packaging,
official EasyHPC upload, and server-copy SHA256 verification.

## Security Rules

Never commit, print, summarize, or include in a package:

- `.env`, `.env.*`, Cookie headers, session values, passwords, API tokens;
- browser local/session storage dumps;
- files named like `*cookie*`, `*session*`, `*secret*`, or `*token*`.

Treat `EASYHPC_COOKIE` and `EASYHPC_SESSION` as passwords. Use them only for
official EasyHPC API calls requested by the user. Never modify, forge, backdate,
or manipulate submission timestamps or server records.

## First Use

Resolve the skill directory first. In a Codex-installed skill this is the
directory containing this `SKILL.md`.

```bash
SKILL_ROOT="$CODEX_HOME/skills/easyhpc-homework"
python "$SKILL_ROOT/scripts/easyhpc_env.py" --env-file "$SKILL_ROOT/.env" show
```

If `.env` is missing or incomplete, ask the user for EasyHPC username/account,
EasyHPC password, student ID, student name, and university, then store them only
in `$SKILL_ROOT/.env` with mode `600`. Prefer this helper when an interactive
terminal is available:

```bash
python "$SKILL_ROOT/scripts/easyhpc_env.py" --env-file "$SKILL_ROOT/.env" init
```

Expected private keys:

```text
EASYHPC_USERNAME=
EASYHPC_PASSWORD=
EASYHPC_STUDENT_ID=
EASYHPC_STUDENT_NAME=
EASYHPC_UNIVERSITY=中山大学
EASYHPC_REPORT_PREFIX=课程作业
EASYHPC_WORK_ROOT=
EASYHPC_COOKIE=
EASYHPC_SESSION=
```

EasyHPC login may require browser verification, so API commands need a fresh
`EASYHPC_COOKIE` or `EASYHPC_SESSION`. If only username/password are available,
ask the user to log in through the browser and provide a current Cookie header
or the `session` cookie value. Do not attempt to bypass CAPTCHA or verification.

## References

Load only the relevant reference:

- Coding/experiment labs: `references/parallel-lab-workflow.md`
- Chinese report style: `references/report-writing-style.md`
- Theory/problem-set homework: `references/theory-homework-workflow.md`

For list/download/upload only, this file plus `scripts/easyhpc_homework.py` is
enough.

## Core CLI

Use the bundled helper. Always avoid printing secrets.

```bash
python "$SKILL_ROOT/scripts/easyhpc_homework.py" --course COURSE_ID --env-file "$SKILL_ROOT/.env" list
python "$SKILL_ROOT/scripts/easyhpc_homework.py" --course COURSE_ID --session "$EASYHPC_SESSION" list
python "$SKILL_ROOT/scripts/easyhpc_homework.py" --course COURSE_ID --cookie-file /path/to/private_cookie.txt list
```

Common commands:

```bash
python "$SKILL_ROOT/scripts/easyhpc_homework.py" --course COURSE_ID --env-file "$SKILL_ROOT/.env" download --unsubmitted --out "$WORK_ROOT/easyhpc_unsubmitted_homework"

python "$SKILL_ROOT/scripts/easyhpc_homework.py" --course COURSE_ID --env-file "$SKILL_ROOT/.env" submissions --homework HOMEWORK_ID

python "$SKILL_ROOT/scripts/easyhpc_homework.py" --course COURSE_ID --env-file "$SKILL_ROOT/.env" upload --homework HOMEWORK_ID --file "$ZIP_PATH" --verify-download --verify-dir "$WORK_ROOT/easyhpc_submit_verification"
```

Use `--replace-existing` only after explicit user approval or when the user has
already authorized replacing existing submissions.

## Required Interaction

Default to autonomous completion. Ask only when the missing input cannot be
recovered from EasyHPC, attachments, local files, or public/course material:

- valid Cookie/session for protected API work;
- course ID or homework ID when ambiguous;
- explicit approval to replace an existing submission;
- private dataset/repository/material not available locally or on EasyHPC.

For first use, ask for account/password and student profile before doing
protected work, then store them in the private `.env`. Do not ask repeatedly if
the stored configuration validates.

## Workflow

1. **Authenticate and list.** Validate the current Cookie/session with a light
   `list` request. On `401`, stop and ask for a fresh session.
2. **Download materials.** Use EasyHPC attachments and course files first.
3. **Extract requirements.** Prefer structured extraction: DOCX XML, ZIP file
   lists, PDF/PPTX text tools, then local notes.
4. **Classify.** If the task asks for code, experiments, runtime, figures,
   speedup, or source submission, follow the programming branch. If it is
   questions/calculation/concept analysis only, follow the theory branch.
5. **Scaffold when useful.**

   ```bash
   python "$SKILL_ROOT/scripts/parallel_lab_scaffold.py" --week WEEK --title "Lab title" --root "$WORK_ROOT"
   python "$SKILL_ROOT/scripts/theory_homework_scaffold.py" --week WEEK --title "Theory homework title" --root "$WORK_ROOT"
   ```

6. **Implement or answer.** For coding labs, compile, run samples, benchmark,
   save CSV, generate English figures, and write a detailed Chinese report. For
   theory tasks, answer every subquestion in Chinese final-exam style and
   compile a readable PDF.
7. **Verify.** Run official/public/local tests when available. If a score exists,
   keep improving until the maximum attainable score is reached or the remaining
   limitation is proven. Compile XeLaTeX at least twice and check for undefined
   references.
8. **Package.** Zip the project and exclude build artifacts, LaTeX aux files,
   pycache, old nested zips, `.env`, cookies, sessions, and secrets.
9. **Upload and verify.** Upload through the official API, download the server
   copy, and compare SHA256 with the local artifact.
10. **Final response.** Report homework ID/title, local zip path, submission ID,
    `Submitted` flag, test/score evidence, SHA256 verification, and any caveat.

## Quality Gates

Programming/experiment homework:

- parse every named requirement before coding;
- compile from a documented command;
- run samples/tests/scorers that are available;
- generate reproducible results, CSV files, and figures;
- include source, report PDF, scripts, results, figures, and AI/session notes if
  the assignment asks for them.

Theory homework:

- do not answer from the title alone;
- recover the actual questions before writing;
- show definitions, formulas, derivations, tables, algorithms, and conclusions
  as needed;
- compile and inspect the PDF before packaging.

Reports must be concrete: environment, code structure, design choices,
commands, outputs, scores, figures, limitations, and AI usage when required.

## EasyHPC API Surface

Known endpoints used by `scripts/easyhpc_homework.py`:

- `GET /api/v1/course/{courseID}/homework`
- `GET /api/v1/course/{courseID}/homework/{homeworkID}/file/{fileID}?stream=true`
- `GET /api/v1/course/{courseID}/homework/{homeworkID}/submission`
- `POST /api/v1/course/{courseID}/homework/{homeworkID}/submission`
- `PUT /api/v1/course/{courseID}/homework/{homeworkID}/submission/{submissionID}`
- `GET /api/v1/course/{courseID}/homework/{homeworkID}/submission/{submissionID}?stream=true`

Upload multipart fields follow the official frontend: `Title`, `Type=0`, and
`File`.
