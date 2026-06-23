#!/usr/bin/env python3
from __future__ import annotations
import json, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

UA = "awesome-agent-metadata/1.0"

def _jget(url: str, token: str | None) -> dict:
    headers = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def fetch_repos_from_sources(sources: list[dict]) -> list[dict]:
    token = os.environ.get("GITHUB_TOKEN")
    merged = {}
    for source in sources:
        data = _jget(source["url"], token)
        items = data.values() if isinstance(data, dict) else data
        for entry in items:
            owner = entry.get("owner") or ""
            name = entry.get("name") or ""
            if owner and name and entry.get("enabled", True):
                merged[f"{owner}/{name}"] = entry
    return list(merged.values())

def _fields(entry: dict) -> dict:
    return {
        "owner": entry.get("owner") or "",
        "name": entry.get("name") or "",
        "branch": entry.get("branch") or "main",
        "path": (entry.get("agentsPath") or "").strip("/"),
    }

def _count_agents(entry: dict, token: str | None) -> dict:
    f = _fields(entry)
    full = f"{f['owner']}/{f['name']}"
    try:
        tree = _jget(f"https://api.github.com/repos/{full}/git/trees/{f['branch']}?recursive=1", token)
    except HTTPError as e:
        status = "missing" if e.code == 404 else "forbidden" if e.code == 403 else "error"
        return {"full": full, "count": 0, "status": status, "note": f"HTTP {e.code}", "branch": f["branch"], "path": f["path"]}
    except (URLError, OSError, TimeoutError) as e:
        return {"full": full, "count": 0, "status": "error", "note": str(e)[:120], "branch": f["branch"], "path": f["path"]}
    count = 0
    base = f["path"]
    for n in tree.get("tree", []):
        if n.get("type") != "blob":
            continue
        p = n["path"]
        if base and not (p.startswith(base + "/") or p == base):
            continue
        fn = p.rsplit("/", 1)[-1]
        if fn.endswith('.md') and fn.lower() != 'readme.md':
            count += 1
    trunc = bool(tree.get("truncated", False))
    return {"full": full, "count": count, "status": "truncated" if trunc else "ok", "note": "tree truncated; count is lower bound" if trunc else "", "branch": f["branch"], "path": f["path"]}

def count_agents(entries: list[dict], max_workers: int = 8) -> dict[str, dict]:
    token = os.environ.get("GITHUB_TOKEN")
    out = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(_count_agents, e, token): e for e in entries}
        for fut in as_completed(futs):
            r = fut.result()
            out[r["full"]] = r
    return out

def render_readme(entries: list[dict], counts: dict[str, dict]) -> str:
    rows = []
    for e in entries:
        f = _fields(e)
        full = f"{f['owner']}/{f['name']}"
        rows.append({**f, **counts.get(full, {"count": 0, "status": "error", "note": "missing count"})})
    rows.sort(key=lambda r: (r["status"] not in {"ok", "truncated"}, r["owner"].lower(), r["name"].lower()))
    total = sum(r["count"] for r in rows)
    ok = sum(1 for r in rows if r["status"] == "ok")
    trunc = sum(1 for r in rows if r["status"] == "truncated")
    bad = len(rows) - ok - trunc
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Awesome Claude Agents",
        "",
        "[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)",
        "",
        "Metadata catalog for Claude agent source repositories. This repo does **not** clone or mirror upstream content; it tracks source repos from [awesome-repo-configs](https://github.com/Chat2AnyLLM/awesome-repo-configs) and counts discoverable agent markdown files via GitHub API.",
        "",
        f"- Enabled source repositories: **{len(rows)}**",
        f"- Discoverable agents: **{total:,}**",
        f"- Healthy repos: **{ok}** · Truncated: **{trunc}** · Unavailable: **{bad}**",
        f"- Last updated: **{ts}**",
        "",
        "## Source Catalog",
        "",
        "| Repository | Agents | Branch | Path | Status | Note |",
        "| --- | ---: | --- | --- | --- | --- |",
    ]
    for r in rows:
        repo = f"[{r['full']}](https://github.com/{r['full']})"
        count = f"≥{r['count']:,}" if r['status'] == 'truncated' else f"{r['count']:,}"
        path = f"`{r['path'] or '.'}`"
        status = {"ok": "✅ ok", "truncated": "⚠️ truncated", "missing": "❌ missing", "forbidden": "⛔ forbidden", "error": "❌ error"}.get(r['status'], r['status'])
        note = (r.get("note") or "").replace("|", "\\|")
        lines.append(f"| {repo} | {count} | `{r['branch']}` | {path} | {status} | {note} |")
    lines += ["", "## Contributing", "", "Add or disable source repositories in [awesome-repo-configs](https://github.com/Chat2AnyLLM/awesome-repo-configs). This repository is a metadata-only catalog."]
    return "\n".join(lines) + "\n"
