#!/usr/bin/env python3
"""Create or inspect the private .env file for the EasyHPC skill."""

from __future__ import annotations

import argparse
import getpass
import os
import shlex
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV = SKILL_ROOT / ".env"
SECRET_KEYS = {"EASYHPC_PASSWORD", "EASYHPC_COOKIE", "EASYHPC_SESSION"}
ORDERED_KEYS = [
    "EASYHPC_USERNAME",
    "EASYHPC_PASSWORD",
    "EASYHPC_COOKIE",
    "EASYHPC_SESSION",
    "EASYHPC_STUDENT_ID",
    "EASYHPC_STUDENT_NAME",
    "EASYHPC_UNIVERSITY",
    "EASYHPC_REPORT_PREFIX",
    "EASYHPC_WORK_ROOT",
]


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        values[key] = value
    return values


def prompt_value(
    key: str,
    label: str,
    existing: dict[str, str],
    *,
    default: str = "",
    secret: bool = False,
    optional: bool = False,
) -> str:
    env_value = os.environ.get(key, "")
    if env_value:
        return env_value
    current = existing.get(key, default)
    suffix = ""
    if current and not secret:
        suffix = f" [{current}]"
    prompt = f"{label}{suffix}: "
    if secret:
        value = getpass.getpass(prompt)
    else:
        value = input(prompt)
    if value:
        return value
    if current:
        return current
    if optional:
        return ""
    raise SystemExit(f"Missing required value: {key}")


def write_env(path: Path, values: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Private EasyHPC skill configuration. Do not commit this file.",
        "# Cookie/session values are login credentials.",
    ]
    for key in ORDERED_KEYS:
        value = values.get(key, "")
        if value:
            lines.append(f"{key}={shlex.quote(value)}")
    text = "\n".join(lines) + "\n"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    os.chmod(path, 0o600)


def cmd_init(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file).expanduser().resolve()
    existing = parse_env(env_path)
    values = dict(existing)
    values["EASYHPC_USERNAME"] = prompt_value(
        "EASYHPC_USERNAME", "EasyHPC username/account", existing
    )
    values["EASYHPC_PASSWORD"] = prompt_value(
        "EASYHPC_PASSWORD", "EasyHPC password", existing, secret=True
    )
    values["EASYHPC_STUDENT_ID"] = prompt_value(
        "EASYHPC_STUDENT_ID", "Student ID", existing
    )
    values["EASYHPC_STUDENT_NAME"] = prompt_value(
        "EASYHPC_STUDENT_NAME", "Student name", existing
    )
    values["EASYHPC_UNIVERSITY"] = prompt_value(
        "EASYHPC_UNIVERSITY", "University", existing, default="中山大学"
    )
    values["EASYHPC_REPORT_PREFIX"] = prompt_value(
        "EASYHPC_REPORT_PREFIX",
        "Course-required report filename prefix",
        existing,
        default="课程作业",
    )
    values["EASYHPC_WORK_ROOT"] = prompt_value(
        "EASYHPC_WORK_ROOT",
        "Default work root",
        existing,
        default=str(Path.cwd()),
        optional=True,
    )
    values["EASYHPC_COOKIE"] = prompt_value(
        "EASYHPC_COOKIE",
        "Optional full Cookie header",
        existing,
        secret=True,
        optional=True,
    )
    if not values.get("EASYHPC_COOKIE"):
        values["EASYHPC_SESSION"] = prompt_value(
            "EASYHPC_SESSION",
            "Optional session cookie value",
            existing,
            secret=True,
            optional=True,
        )
    write_env(env_path, values)
    print(f"Wrote private configuration: {env_path}")
    print("Secrets are not displayed. File mode is 600.")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file).expanduser().resolve()
    values = parse_env(env_path)
    print(f"env_file\t{env_path}")
    for key in ORDERED_KEYS:
        if key in SECRET_KEYS:
            status = "set" if values.get(key) else "missing"
            print(f"{key}\t{status}")
        else:
            print(f"{key}\t{values.get(key, '') or 'missing'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", default=str(DEFAULT_ENV))
    sub = parser.add_subparsers(dest="command", required=True)
    p_init = sub.add_parser("init", help="Interactively create a private .env.")
    p_init.set_defaults(func=cmd_init)
    p_show = sub.add_parser("show", help="Show which config keys are set.")
    p_show.set_defaults(func=cmd_show)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
