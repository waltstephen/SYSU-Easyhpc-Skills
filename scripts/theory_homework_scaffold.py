#!/usr/bin/env python3
"""Create a standard Chinese PDF skeleton for theory-only EasyHPC homework."""

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
    (project / "report").mkdir(parents=True, exist_ok=True)

    write_if_missing(
        project / "Makefile",
        f"""PACKAGE_NAME := 第{args.week}周作业_{student_id}_{student_name}

.PHONY: report package clean

report:
\tcd report && xelatex -interaction=nonstopmode -halt-on-error main.tex && xelatex -interaction=nonstopmode -halt-on-error main.tex
\tcp report/main.pdf "{report_prefix}_{student_id}_{student_name}.pdf"
\tcp report/main.pdf "$(PACKAGE_NAME).pdf"

package:
\tcd .. && zip -r "$(PACKAGE_NAME).zip" "$(PACKAGE_NAME)" -x '$(PACKAGE_NAME)/*.zip' '$(PACKAGE_NAME)/.env' '$(PACKAGE_NAME)/*cookie*' '$(PACKAGE_NAME)/*session*' '$(PACKAGE_NAME)/report/*.aux' '$(PACKAGE_NAME)/report/*.log' '$(PACKAGE_NAME)/report/*.out' '$(PACKAGE_NAME)/report/*.toc'

clean:
\trm -f report/*.aux report/*.log report/*.out report/*.toc
""",
    )

    write_if_missing(
        project / "answer.md",
        f"""# 第 {args.week} 周理论作业

学号：{student_id}
姓名：{student_name}

## 第 1 题

题目分析：

解答：

结论：
""",
    )

    write_if_missing(
        project / "report" / "main.tex",
        rf"""\documentclass[UTF8,a4paper,zihao=-4]{{ctexart}}
\usepackage[margin=2.5cm]{{geometry}}
\usepackage{{amsmath,amssymb,booktabs,graphicx,float,hyperref}}
\hypersetup{{colorlinks=true,linkcolor=blue!60!black,urlcolor=blue!60!black}}

\title{{\textbf{{{args.title}}}}}
\author{{{student_name}\\学号：{student_id}\\{university}}}
\date{{{args.date}}}

\begin{{document}}
\maketitle

\section*{{第 1 题}}

\textbf{{题目分析：}}
本题主要考查……。解题时需要先明确……，再根据……进行分析。

\textbf{{解答：}}
首先，……。

根据……，可得……。

因此，……。

\textbf{{结论：}}
……。

\end{{document}}
""",
    )

    print(project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
