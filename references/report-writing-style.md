# Chinese Lab Report Style

Use this reference for the report voice and structure. Student identity must
come from `EASYHPC_STUDENT_ID`, `EASYHPC_STUDENT_NAME`, and
`EASYHPC_UNIVERSITY`; the course-required report prefix should come from
`EASYHPC_REPORT_PREFIX`. Never hardcode private identity or course identifiers
into the public skill.

## Tone

Write in Chinese like a serious undergraduate lab report:

- use natural phrases such as “本实验”, “我在实验中”, and “从结果可以看到”;
- keep the tone formal but not paper-like;
- analyze the actual code, data, commands, figures, and observed results;
- avoid inflated claims such as “极大提升性能” or “完美实现”;
- honestly explain weak speedup, overhead, failed cases, or limitations.

Good style:

```text
从实验结果可以看到，在较小规模下，多线程版本并没有稳定获得加速。我认为主要原因是每个线程实际承担的计算量不大，而线程创建、调度和同步本身需要时间。当矩阵规模增大后，计算部分占比提高，多线程带来的收益才更明显。
```

Bad style:

```text
本算法具有极高性能，充分体现了并行计算的巨大优势。
```

## Structure

Recommended sections:

1. 实验目的
2. 实验环境
3. 理论背景
4. 算法与并行设计
5. 具体实现
6. 编译与运行方式
7. 实验结果
8. 性能分析
9. 问题与改进
10. 总结

If there are multiple tasks, split the body by task and add a final comparison.

## Content Expectations

Theory background should support the experiment, not become an encyclopedia.
Mention only the concepts needed to understand the implementation and results.

Implementation should explain:

- source files and their roles;
- command-line parameters;
- data initialization;
- thread/process partitioning;
- synchronization or race avoidance;
- timing method;
- correctness verification.

Results must cite real artifacts:

- raw data from `results/*.csv`;
- figures from `figures/*.png`;
- formulas for speedup and efficiency;
- concrete explanations for abnormal or weak results.

Summary should cover what was completed, what the data shows, and what could be
improved.

## XeLaTeX Convention

Use `ctexart`:

```tex
\documentclass[UTF8,a4paper,zihao=-4]{ctexart}
\usepackage[margin=2.5cm]{geometry}
\usepackage{amsmath,amssymb,booktabs,graphicx,float,listings,hyperref}
```

Tables should use `booktabs`. Figures can have English labels inside the image,
while captions and analysis remain Chinese.

Compile and check:

```bash
cd report
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
pdfinfo main.pdf
grep -c "undefined" main.log
```
