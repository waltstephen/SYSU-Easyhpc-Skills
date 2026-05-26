# Parallel Lab Workflow

Use this reference for EasyHPC programming or experiment labs.

Student identity comes from private configuration:

```text
EASYHPC_STUDENT_ID
EASYHPC_STUDENT_NAME
EASYHPC_UNIVERSITY
EASYHPC_REPORT_PREFIX
```

Final PDF names should normally be:

```text
${EASYHPC_REPORT_PREFIX}_${EASYHPC_STUDENT_ID}_${EASYHPC_STUDENT_NAME}.pdf
第N周作业_${EASYHPC_STUDENT_ID}_${EASYHPC_STUDENT_NAME}.pdf
```

## Recommended Project Layout

```text
第N周作业_${EASYHPC_STUDENT_ID}_${EASYHPC_STUDENT_NAME}/
├── Makefile
├── code_description.md
├── src/
├── tools/ or scripts/
│   └── run_benchmarks.py
├── results/
├── figures/
├── report/
│   ├── main.tex
│   └── generated_tables.tex
├── ${EASYHPC_REPORT_PREFIX}_${EASYHPC_STUDENT_ID}_${EASYHPC_STUDENT_NAME}.pdf
└── 第N周作业_${EASYHPC_STUDENT_ID}_${EASYHPC_STUDENT_NAME}.pdf
```

Include extra files only when required by the assignment, such as shared
libraries, reference code, datasets, or teacher-provided scripts.

## Implementation Order

1. Read the assignment from DOCX/PPTX/PDF/ZIP and record inputs, outputs,
   thread/process counts, scale ranges, required API, synchronization rules,
   report requirements, and packaging requirements.
2. Implement correctness first, then CLI parameters, timing, validation, and
   error handling.
3. Test small cases such as tiny matrices, short arrays, few samples, or low
   iteration counts.
4. Benchmark common thread counts such as `1,2,4,8`; use assignment-specified
   sizes and repeat runs when results are noisy.
5. Save raw results to CSV and compute:

   ```text
   Speedup(p) = T1 / Tp
   Efficiency(p) = Speedup(p) / p
   ```

6. Generate figures with English titles, axis labels, and legends.
7. Write a Chinese XeLaTeX report that explains design, implementation,
   commands, verification, results, performance, and limitations.
8. Package source, report PDF, scripts, CSV, figures, and required original
   material. Exclude build artifacts and secrets.
9. Upload via EasyHPC and verify the downloaded server copy by SHA256.

## Pthreads Notes

Explain thread partitioning, shared data, mutexes, condition variables, and
`pthread_join` aggregation. Common patterns:

- independent rows/ranges: each thread owns a contiguous slice;
- reductions: local accumulators plus final aggregation;
- dynamic work: shared `next` index protected by a mutex;
- dependency-heavy tasks: `pthread_mutex_t` plus `pthread_cond_t`.

If results do not speed up, discuss problem size, thread creation overhead,
synchronization, memory bandwidth, load balance, or dependency bottlenecks.

## OpenMP Notes

Common constructs:

```c
#pragma omp parallel for
#pragma omp parallel for schedule(static, 1)
#pragma omp parallel for schedule(dynamic, 1)
```

Discuss default scheduling, static scheduling overhead, dynamic scheduling for
load imbalance, reduction clauses, and runtime overhead.

## Common Experiment Templates

Matrix multiplication:

- explain `C=A*B`, complexity, row/block partitioning, and write ownership;
- verify checksum or small reference results;
- compare runtime, speedup, efficiency, and scheduling.

Array reduction:

- use local sums to reduce lock contention;
- show how scale affects speedup.

Monte Carlo Pi:

- use per-thread RNG state;
- explain convergence and final aggregation.

Heated plate:

- explain stencil update, iteration dependency, convergence criterion;
- compare Pthreads/OpenMP or static/dynamic scheduling when required.

## Makefile Targets

Use predictable targets:

```makefile
all:
benchmark:
report:
package:
clean:
```

`report` should compile XeLaTeX twice and copy the PDF to the course-required
name and the week-name. `package` should exclude:

```text
build/*
report/*.aux
report/*.log
report/*.out
report/*.toc
**/__pycache__/*
*.zip
.env
*cookie*
*session*
*secret*
*token*
```

## Verification Checklist

- `make all` succeeds.
- Small correctness tests pass.
- Benchmark creates CSV and figures.
- XeLaTeX produces a readable PDF.
- `grep -c "undefined" report/main.log` is `0`.
- Zip contains required PDF, source, instructions, scripts, results, and figures.
- Uploaded server copy has the same SHA256 as the local zip.
