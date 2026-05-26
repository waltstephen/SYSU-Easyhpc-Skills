#!/usr/bin/env python3
"""Create a standard EasyHPC lab project skeleton.

This script intentionally does not implement the lab. It creates the directory
layout, a Makefile shell, code description stub, benchmark script stub, and a
Chinese XeLaTeX report template using identity values from arguments or .env.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def dotenv_value(key: str) -> str:
    for path in [Path.cwd() / ".env", SKILL_ROOT / ".env"]:
        if not path.is_file():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            if name.strip() != key:
                continue
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            return value
    return ""


def config_value(args: argparse.Namespace, attr: str, key: str, default: str = "") -> str:
    return getattr(args, attr) or os.environ.get(key, "") or dotenv_value(key) or default


def report_date() -> str:
    today = dt.date.today()
    return f"{today.year} 年 {today.month} 月"


def write_if_missing(path: Path, text: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week", required=True, type=int)
    parser.add_argument("--title", required=True)
    parser.add_argument("--root", default=os.environ.get("EASYHPC_WORK_ROOT") or str(Path.cwd()))
    parser.add_argument("--student-id")
    parser.add_argument("--student-name")
    parser.add_argument("--university")
    parser.add_argument("--report-prefix")
    parser.add_argument("--date", default=report_date())
    args = parser.parse_args()

    student_id = config_value(args, "student_id", "EASYHPC_STUDENT_ID")
    student_name = config_value(args, "student_name", "EASYHPC_STUDENT_NAME")
    university = config_value(args, "university", "EASYHPC_UNIVERSITY", "中山大学")
    report_prefix = config_value(
        args, "report_prefix", "EASYHPC_REPORT_PREFIX", "课程作业"
    )
    missing = [
        key
        for key, value in [
            ("EASYHPC_STUDENT_ID", student_id),
            ("EASYHPC_STUDENT_NAME", student_name),
        ]
        if not value
    ]
    if missing:
        raise SystemExit(
            "Missing student profile. Set "
            + ", ".join(missing)
            + " in .env or pass --student-id/--student-name."
        )

    project = Path(args.root) / f"第{args.week}周作业_{student_id}_{student_name}"
    for dirname in ["src", "tools", "results", "figures", "report", "build"]:
        (project / dirname).mkdir(parents=True, exist_ok=True)

    write_if_missing(
        project / "Makefile",
        f"""CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -std=c11
PACKAGE_NAME := 第{args.week}周作业_{student_id}_{student_name}

.PHONY: all benchmark report package clean

all:
\t@echo "TODO: add build targets"

benchmark: all
\tpython3 tools/run_benchmarks.py

report:
\tcd report && xelatex -interaction=nonstopmode -halt-on-error main.tex && xelatex -interaction=nonstopmode -halt-on-error main.tex
\tcp report/main.pdf "{report_prefix}_{student_id}_{student_name}.pdf"
\tcp report/main.pdf "$(PACKAGE_NAME).pdf"

package:
\tcd .. && zip -r "$(PACKAGE_NAME).zip" "$(PACKAGE_NAME)" -x '$(PACKAGE_NAME)/*.zip' '$(PACKAGE_NAME)/.env' '$(PACKAGE_NAME)/*cookie*' '$(PACKAGE_NAME)/*session*' '$(PACKAGE_NAME)/build/*' '$(PACKAGE_NAME)/**/__pycache__/*' '$(PACKAGE_NAME)/report/*.aux' '$(PACKAGE_NAME)/report/*.log' '$(PACKAGE_NAME)/report/*.out' '$(PACKAGE_NAME)/report/*.toc'

clean:
\trm -rf build
\trm -f report/*.aux report/*.log report/*.out report/*.toc
""",
    )

    write_if_missing(
        project / "code_description.md",
        f"""# 代码说明

## 实验信息

- 第 {args.week} 周作业
- 题目：{args.title}
- 学号：{student_id}
- 姓名：{student_name}

## 文件说明

在此说明 `src/` 下每个源码文件的功能、输入输出、并行策略、同步方式和验证方法。
""",
    )

    write_if_missing(
        project / "tools" / "run_benchmarks.py",
        """#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "figures").mkdir(exist_ok=True)
    (ROOT / "report").mkdir(exist_ok=True)
    raise SystemExit("TODO: implement benchmark, CSV export, figures, and report/generated_tables.tex")


if __name__ == "__main__":
    main()
""",
    )

    write_if_missing(
        project / "report" / "main.tex",
        rf"""\documentclass[UTF8,a4paper,zihao=-4]{{ctexart}}
\usepackage[margin=2.5cm]{{geometry}}
\usepackage{{amsmath,amssymb,booktabs,graphicx,float,listings,hyperref}}
\graphicspath{{{{../figures/}}}}
\lstset{{basicstyle=\ttfamily\small,breaklines=true,columns=fullflexible,frame=single,keepspaces=true}}

\title{{\textbf{{课程实验报告\\第{args.week}周：{args.title}}}}}
\author{{{student_name}\\学号：{student_id}\\{university}}}
\date{{{args.date}}}

\begin{{document}}
\maketitle
\tableofcontents
\newpage

\section{{实验目的}}

本实验围绕“{args.title}”展开，目标是理解相关并行模型的基本使用方法，并通过实验结果分析线程数、调度方式、同步开销和任务规模对性能的影响。

\section{{实验环境}}

\begin{{table}}[H]
\centering
\caption{{实验环境}}
\begin{{tabular}}{{ll}}
\toprule
项目 & 内容 \\
\midrule
操作系统 & Linux \\
编译器 & gcc \\
编译参数 & 待填写 \\
CPU 型号 & 待填写 \\
CPU 核心数 & 待填写 \\
内存 & 待填写 \\
\bottomrule
\end{{tabular}}
\end{{table}}

\section{{理论背景}}

待补充本实验涉及的算法原理、并行模型和性能指标。

\section{{具体实现}}

待说明源码结构、线程划分、同步方式、计时方式和正确性验证。

\section{{实验结果}}

\input{{generated_tables.tex}}

\section{{性能分析}}

待结合表格和图说明运行时间、加速比、并行效率以及异常结果的原因。

\section{{总结}}

待总结完成内容、结果结论和可以继续改进的方向。

\end{{document}}
""",
    )

    write_if_missing(project / "report" / "generated_tables.tex", "% generated by tools/run_benchmarks.py\n")

    print(project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
