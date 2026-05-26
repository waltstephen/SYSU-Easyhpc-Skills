# Theory Homework Workflow

Use this reference when an EasyHPC assignment is a theory/problem-set task:
concept questions, calculations, comparisons, algorithm hand analysis, or short
answers without required code, experiments, or figures.

Student identity comes from private `.env` keys:

```text
EASYHPC_STUDENT_ID
EASYHPC_STUDENT_NAME
EASYHPC_UNIVERSITY
```

## Goal

1. Recover the actual questions from EasyHPC materials.
2. Analyze the examined concepts and formulas.
3. Write clear Chinese final-exam-style answers.
4. Compile a readable PDF.
5. Package and submit according to EasyHPC requirements.

## Workflow

1. **Extract questions.** Use DOCX/PDF/PPTX extraction, attachments, local
   notes, and previous official material. Do not answer from the filename alone.
2. **Analyze each question.** Identify the concept, definition, formula,
   algorithm, comparison axis, assumptions, and possible traps.
3. **Answer in exam style.** Give the key definition or formula, then derivation
   or reasoning, then a clear conclusion. Use tables for comparisons and show
   calculation steps for numeric questions.
4. **Generate PDF.** Use `ctexart`. Keep the answer readable and not overly
   verbose.
5. **Package.** Include the PDF, `report/main.tex`, and optional draft notes.
   Exclude `.env`, cookies, sessions, and secrets.
6. **Upload and verify.** Use `easyhpc_homework.py upload --verify-download` and
   compare SHA256.

## Answer Template

```text
第 1 题

题目分析：
本题主要考查……。关键点是……。

解答：
首先，……。
根据公式……，可得……。
因此，……。

结论：
……。
```

For many short questions, compress “题目分析” into one sentence to avoid a
fragmented report.

## Common Question Types

Concept explanation:

- definition;
- purpose;
- short example or contrast.

Comparison:

- use a table when there are several dimensions;
- explicitly state advantages, disadvantages, and applicable scenarios.

Calculation:

- write formulas;
- substitute numbers;
- state units and final result.

Algorithm analysis:

- input and output;
- main steps;
- time complexity;
- parallelizable parts;
- synchronization or dependency bottleneck.

## PDF Check

```bash
pdfinfo report/main.pdf
grep -c "undefined" report/main.log
```

The PDF should open normally, have a reasonable page count, and contain no
obvious `??`, missing formulas, or severe overflow.
