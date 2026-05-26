#!/usr/bin/env python3
"""EasyHPC homework helper.

The script intentionally avoids third-party dependencies and never prints
credentials. Provide authentication via EASYHPC_COOKIE/EASYHPC_SESSION, --cookie,
--session, or a local .env file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_BASE = "https://www.easyhpc.net/api/v1"


class EasyHPCError(RuntimeError):
    pass


def dotenv_value(key: str, env_file: str | None = None) -> str:
    candidates = [
        Path(env_file).expanduser() if env_file else None,
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[1] / ".env",
    ]
    for path in candidates:
        if path is None:
            continue
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


def normalize_cookie(args: argparse.Namespace) -> str:
    env_file = getattr(args, "env_file", None)
    cookie = (
        args.cookie
        or os.environ.get("EASYHPC_COOKIE", "")
        or dotenv_value("EASYHPC_COOKIE", env_file)
    )
    if args.cookie_file:
        cookie = Path(args.cookie_file).read_text(encoding="utf-8").strip()
    session = (
        args.session
        or os.environ.get("EASYHPC_SESSION", "")
        or dotenv_value("EASYHPC_SESSION", env_file)
    )
    if session:
        cookie = f"session={session}; SESSION_ID=A"
    if args.session:
        cookie = f"session={args.session}; SESSION_ID=A"
    cookie = cookie.strip()
    if not cookie:
        has_password_profile = bool(
            os.environ.get("EASYHPC_USERNAME")
            or dotenv_value("EASYHPC_USERNAME", env_file)
            or os.environ.get("EASYHPC_PASSWORD")
            or dotenv_value("EASYHPC_PASSWORD", env_file)
        )
        if has_password_profile:
            raise EasyHPCError(
                "Missing Cookie/session. A username/password profile exists, "
                "but API calls need EASYHPC_COOKIE or EASYHPC_SESSION because "
                "EasyHPC login can require browser verification."
            )
        raise EasyHPCError(
            "Missing Cookie/session. Set EASYHPC_COOKIE, EASYHPC_SESSION, "
            "or pass --cookie/--session."
        )
    if "session=" not in cookie and "SESSION_ID=" not in cookie:
        cookie = f"session={cookie}; SESSION_ID=A"
    return cookie


def request(
    method: str,
    path: str,
    cookie: str,
    *,
    query: dict[str, str] | None = None,
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 120,
) -> tuple[int, dict[str, str], bytes]:
    url = f"{API_BASE}{path}"
    if query:
        url = f"{url}?{urlencode(query)}"
    req_headers = {
        "Cookie": cookie,
        "User-Agent": "easyhpc-homework-skill/1.0",
    }
    if headers:
        req_headers.update(headers)
    req = Request(url, data=body, headers=req_headers, method=method.upper())
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except HTTPError as exc:
        data = exc.read()
        raise EasyHPCError(
            f"HTTP {exc.code} for {method} {path}: {data[:300]!r}"
        ) from exc
    except URLError as exc:
        raise EasyHPCError(f"Network error for {method} {path}: {exc}") from exc


def get_json(method: str, path: str, cookie: str, **kwargs: Any) -> Any:
    _status, _headers, data = request(method, path, cookie, **kwargs)
    try:
        return json.loads(data.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise EasyHPCError(f"Expected JSON from {path}, got: {data[:300]!r}") from exc


def slug(text: str) -> str:
    text = text.strip().replace("/", "_").replace("\\", "_")
    text = re.sub(r"[\r\n\t]+", " ", text)
    return text or "untitled"


def homework_list(course: str, cookie: str) -> dict[str, Any]:
    return get_json("GET", f"/course/{course}/homework", cookie)


def find_homework(data: dict[str, Any], homework_id: int) -> dict[str, Any]:
    for item in data.get("List", []):
        if int(item.get("ID", -1)) == homework_id:
            return item
    raise EasyHPCError(f"Homework {homework_id} not found in course list.")


def print_homework_table(data: dict[str, Any], only_unsubmitted: bool = False) -> None:
    print("ID\tTitle\tDueTime\tSubmitted\tCorrected\tFiles")
    for item in data.get("List", []):
        if only_unsubmitted and int(item.get("Submitted", 0)) != 0:
            continue
        print(
            "\t".join(
                [
                    str(item.get("ID", "")),
                    str(item.get("Title", "")),
                    str(item.get("DueTime", "")),
                    str(item.get("Submitted", "")),
                    str(item.get("Corrected", "")),
                    str(len(item.get("Files") or [])),
                ]
            )
        )


def download_file(course: str, homework_id: int, file_id: int, cookie: str) -> bytes:
    _status, _headers, data = request(
        "GET",
        f"/course/{course}/homework/{homework_id}/file/{file_id}",
        cookie,
        query={"stream": "true"},
        timeout=180,
    )
    return data


def cmd_list(args: argparse.Namespace, cookie: str) -> None:
    data = homework_list(args.course, cookie)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_homework_table(data, args.unsubmitted)


def cmd_download(args: argparse.Namespace, cookie: str) -> None:
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    data = homework_list(args.course, cookie)
    (out / "homework_list.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    selected_ids = {int(x) for x in args.homework} if args.homework else None
    manifest_lines = []
    count = 0
    for hw in data.get("List", []):
        hwid = int(hw["ID"])
        if selected_ids is not None and hwid not in selected_ids:
            continue
        if args.unsubmitted and int(hw.get("Submitted", 0)) != 0:
            continue
        hw_dir = out / f"{hwid}_{slug(str(hw.get('Title', 'homework')))}"
        hw_dir.mkdir(parents=True, exist_ok=True)
        for file_info in hw.get("Files") or []:
            fid = int(file_info["ID"])
            name = slug(str(file_info.get("Name", fid)))
            expected = int(file_info.get("Size", 0))
            target = hw_dir / f"{fid}_{name}"
            data_bytes = download_file(args.course, hwid, fid, cookie)
            target.write_bytes(data_bytes)
            actual = target.stat().st_size
            if expected and actual != expected:
                raise EasyHPCError(
                    f"Size mismatch for {target}: expected {expected}, got {actual}"
                )
            manifest_lines.append(
                f"{hwid}\t{hw.get('Title', '')}\t{fid}\t{name}\t{actual}\t{target}"
            )
            print(f"OK\t{hwid}\t{fid}\t{actual}\t{target}")
            count += 1
    (out / "download_manifest.tsv").write_text(
        "homework_id\thomework_title\tfile_id\tfile_name\tsize\tpath\n"
        + "\n".join(manifest_lines)
        + ("\n" if manifest_lines else ""),
        encoding="utf-8",
    )
    print(f"Downloaded {count} file(s) into {out}")


def submissions(course: str, homework_id: int, cookie: str) -> dict[str, Any]:
    return get_json("GET", f"/course/{course}/homework/{homework_id}/submission", cookie)


def cmd_submissions(args: argparse.Namespace, cookie: str) -> None:
    for hwid in args.homework:
        data = submissions(args.course, int(hwid), cookie)
        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
            continue
        print(f"# homework {hwid}")
        print("ID\tCreatedAt\tTitle\tType")
        for item in data.get("List", []):
            print(
                "\t".join(
                    [
                        str(item.get("ID", "")),
                        str(item.get("CreatedAt", "")),
                        str(item.get("Title", "")),
                        str(item.get("Type", "")),
                    ]
                )
            )


def multipart(fields: dict[str, str], files: dict[str, Path]) -> tuple[bytes, str]:
    boundary = f"----easyhpc-{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                str(value).encode("utf-8"),
                b"\r\n",
            ]
        )
    for field, path in files.items():
        filename = path.name
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                (
                    f'Content-Disposition: form-data; name="{field}"; '
                    f'filename="{filename}"\r\n'
                ).encode("utf-8"),
                f"Content-Type: {content_type}\r\n\r\n".encode(),
                path.read_bytes(),
                b"\r\n",
            ]
        )
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), boundary


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def create_or_replace_submission(
    course: str,
    homework_id: int,
    zip_path: Path,
    cookie: str,
    *,
    replace_existing: bool,
) -> tuple[str, int, dict[str, Any]]:
    current = submissions(course, homework_id, cookie)
    existing = current.get("List") or []
    body, boundary = multipart({"Title": "", "Type": "0"}, {"File": zip_path})
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    if existing:
        if not replace_existing:
            ids = ", ".join(str(x.get("ID")) for x in existing)
            raise EasyHPCError(
                f"Homework {homework_id} already has submission(s): {ids}. "
                "Use --replace-existing only after explicit user approval."
            )
        submission_id = int(existing[0]["ID"])
        status, _headers, data = request(
            "PUT",
            f"/course/{course}/homework/{homework_id}/submission/{submission_id}",
            cookie,
            body=body,
            headers=headers,
            timeout=180,
        )
        action = "replace"
    else:
        status, _headers, data = request(
            "POST",
            f"/course/{course}/homework/{homework_id}/submission",
            cookie,
            body=body,
            headers=headers,
            timeout=180,
        )
        action = "create"
    response: dict[str, Any]
    try:
        response = json.loads(data.decode("utf-8")) if data else {}
    except json.JSONDecodeError:
        response = {"raw": data.decode("utf-8", errors="replace")}
    return action, status, response


def download_submission(
    course: str, homework_id: int, submission_id: int, cookie: str, target: Path
) -> None:
    _status, _headers, data = request(
        "GET",
        f"/course/{course}/homework/{homework_id}/submission/{submission_id}",
        cookie,
        query={"stream": "true"},
        timeout=180,
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def cmd_upload(args: argparse.Namespace, cookie: str) -> None:
    zip_path = Path(args.file).resolve()
    if not zip_path.is_file():
        raise EasyHPCError(f"Upload file not found: {zip_path}")
    hwid = int(args.homework)
    hw_data = homework_list(args.course, cookie)
    hw = find_homework(hw_data, hwid)
    action, status, response = create_or_replace_submission(
        args.course,
        hwid,
        zip_path,
        cookie,
        replace_existing=args.replace_existing,
    )
    print(f"{action}\tHTTP {status}\thomework={hwid}\tfile={zip_path}")
    print(json.dumps(response, ensure_ascii=False, indent=2))
    # Let the backend settle before reading the submission list.
    time.sleep(1)
    sub_data = submissions(args.course, hwid, cookie)
    print("Submission list after upload:")
    print(json.dumps(sub_data, ensure_ascii=False, indent=2))
    final_list = homework_list(args.course, cookie)
    final_hw = find_homework(final_list, hwid)
    print(
        "Homework flag after upload:\t"
        f"{final_hw.get('ID')}\t{final_hw.get('Title')}\t"
        f"Submitted={final_hw.get('Submitted')}\tCorrected={final_hw.get('Corrected')}"
    )
    if args.verify_download:
        items = sub_data.get("List") or []
        if not items:
            raise EasyHPCError("No submission found after upload; cannot verify.")
        submission_id = int(items[0]["ID"])
        if action == "create" and response.get("ID"):
            submission_id = int(response["ID"])
        verify_dir = Path(args.verify_dir).resolve()
        downloaded = verify_dir / f"{args.course}_{hwid}_{submission_id}_{zip_path.name}"
        download_submission(args.course, hwid, submission_id, cookie, downloaded)
        local_hash = sha256(zip_path)
        remote_hash = sha256(downloaded)
        print(f"SHA256 local:\t{local_hash}")
        print(f"SHA256 remote:\t{remote_hash}")
        if local_hash != remote_hash:
            raise EasyHPCError(
                f"Downloaded server copy differs from local file: {downloaded}"
            )
        print(f"Verified server copy matches local file:\t{downloaded}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--course", required=True, help="EasyHPC course ID.")
    parser.add_argument("--env-file", help="Path to a private .env file.")
    parser.add_argument("--cookie", help="Full Cookie header value.")
    parser.add_argument("--cookie-file", help="Path containing a Cookie header value.")
    parser.add_argument("--session", help="Session cookie value only.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List homework.")
    p_list.add_argument("--unsubmitted", action="store_true")
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_download = sub.add_parser("download", help="Download homework materials.")
    p_download.add_argument("--out", required=True)
    p_download.add_argument("--unsubmitted", action="store_true")
    p_download.add_argument("--homework", action="append", default=[])
    p_download.set_defaults(func=cmd_download)

    p_sub = sub.add_parser("submissions", help="List homework submissions.")
    p_sub.add_argument("--homework", action="append", required=True)
    p_sub.add_argument("--json", action="store_true")
    p_sub.set_defaults(func=cmd_submissions)

    p_upload = sub.add_parser("upload", help="Upload a completed homework zip.")
    p_upload.add_argument("--homework", required=True)
    p_upload.add_argument("--file", required=True)
    p_upload.add_argument("--replace-existing", action="store_true")
    p_upload.add_argument("--verify-download", action="store_true")
    p_upload.add_argument(
        "--verify-dir",
        default=os.environ.get(
            "EASYHPC_VERIFY_DIR", str(Path.cwd() / "easyhpc_submit_verification")
        ),
    )
    p_upload.set_defaults(func=cmd_upload)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        cookie = normalize_cookie(args)
        args.func(args, cookie)
    except EasyHPCError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
