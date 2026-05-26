# Codex Homework Guide

This guide shows how to ask Codex to use the EasyHPC homework skill without
putting private course IDs, student IDs, passwords, or cookies in a public
prompt.

## Before First Use

Ask Codex to initialize the private configuration:

```text
Use the easyhpc-homework skill. This is first use. Ask me for the EasyHPC
account/password and student profile, store them only in the skill's private
.env file with permission 600, and do not print any secret values.
```

After logging in to EasyHPC in a browser, provide Codex with a fresh Cookie
header or the `session` cookie value in the active chat only. Do not put it in
source files, public docs, screenshots, or issue comments.

## Minimal Prompt

```text
Use the easyhpc-homework skill. COURSE_ID is <COURSE_ID>. HOMEWORK_ID is
<HOMEWORK_ID>. Download the materials, read the requirements, complete the
homework end to end, generate the required report/package, and verify locally.
Before replacing any existing submission, ask me first.
```

## Finish All Unsubmitted Work

```text
Use the easyhpc-homework skill. COURSE_ID is <COURSE_ID>. List unsubmitted
homework, download the current materials, identify what each task requires, and
complete the next unsubmitted task end to end. Ask me before uploading or
replacing anything.
```

## Coding Lab Prompt

```text
Use the easyhpc-homework skill. COURSE_ID is <COURSE_ID>, HOMEWORK_ID is
<HOMEWORK_ID>. This is a coding/experiment lab. Parse every requirement from
the attachments, implement the code, compile it, run correctness tests and
benchmarks, generate CSV/figures, write a Chinese XeLaTeX report, package the
submission, and show me the verification evidence before upload.
```

## Theory Homework Prompt

```text
Use the easyhpc-homework skill. COURSE_ID is <COURSE_ID>, HOMEWORK_ID is
<HOMEWORK_ID>. This is a theory/problem-set assignment. Recover the actual
questions from EasyHPC materials, answer every subquestion in Chinese
final-exam style with formulas or derivations where needed, compile a readable
PDF, package it, and show me the verification evidence before upload.
```

## Upload Prompt

```text
Use the easyhpc-homework skill. COURSE_ID is <COURSE_ID>, HOMEWORK_ID is
<HOMEWORK_ID>, and the local package is <ZIP_PATH>. Upload it through the
official EasyHPC API, download the server copy, compare SHA256, and report the
submission ID and final Submitted flag. If a previous submission exists, ask me
before replacing it.
```

## What To Give Codex

Provide only what is needed for the current task:

- `COURSE_ID` and `HOMEWORK_ID` when known;
- a fresh Cookie/session for protected EasyHPC operations;
- the local zip path for upload-only tasks;
- explicit approval if an existing submission should be replaced.

Do not paste GitHub tokens, permanent passwords, or unrelated credentials into
the prompt. If a secret is needed, ask Codex to store it only in the private
`.env` and to report only whether it is present and accepted.
