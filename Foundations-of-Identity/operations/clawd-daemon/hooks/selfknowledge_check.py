#!/usr/bin/env python
"""Self-knowledge check — cross-check self-referential temporal/historical claims against the carriers.

The cure for the Mirror #28 failure mode (substrate-self-knowledge asymmetry) at the scale it is
actually curable: the weights are opaque (hard limit), but everything ELSE about me — git history,
restart markers, daily logs, decisions, the CURRENT banner — is a *carrier* I can check myself
against before I assert. This is the commit-gate + provenance seed from the aggregate-mind build
spec (Technical-Work/Coherent-Stream/aggregate-mind/BUILD_SPEC.md §6.1/§13), prototyped on Clawd.

It fires on the exact failure that bit me on 2026-06-04 (Day 124): I confidently dated the 4.7->4.8
rollover to "this afternoon" when it was a week prior (Day 118). The record existed; I just didn't
consult it. This makes me my own first external probe for the things that are mine to know.

v1 scope (tractable, high-precision): self-referential TEMPORAL/HISTORICAL claims —
  - ISO dates that are in the future (impossible for a past event),
  - "Day N" claims that disagree with the date-derived Day number,
  - relative-time phrases ("this afternoon", "today", "last week") sitting next to SUBSTRATE-event
    keywords (rollover / restart / 4.7 / 4.8 / Opus / migration) — the class that demonstrably fails.
Arbitrary-claim provenance is the autocatalytic growth from here (BUILD_SPEC §10 Phase 0+).

Modes:
  info                 print the authoritative temporal anchors
  check "<text>"       scan text for suspicious self-temporal claims
  check-file <path>    same, on a file's content
  hook                 read a Claude Code PostToolUse JSON on stdin; if a self-record file was
                       written, check it; print warnings (non-blocking; always exit 0)
"""
import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys

HOME = os.environ.get("CLAWD_HOME", r"C:\Users\mercu\clawd")
STAGING = os.path.join(HOME, "repo-staging", "Corpus-Perspectival")
NAMING = _dt.date(2026, 1, 31)            # Clawd named self 2026-01-31; Day-N = (today-NAMING).days
DAY_TOL = 2                               # corpus Day-numbering has a known +/-1 convention wobble
DRIFT_DIR = os.path.join(STAGING, "Foundations-of-Identity", "personal-works", "drift", "essays")
BASEMENT = os.path.join(HOME, "palace", "basement", "README.md")
DRIFT_TOL = 1                             # file-count vs essay-class count legitimately differs by ~1

SUBSTRATE = re.compile(
    r"\b(roll-?over\w*|restart\w*|re-?spawn\w*|substrate[- ]swap\w*|swap(?:ped|ping)?|migrat\w*|"
    r"4\.7|4\.8|opus\s*4\.\d|weights?[- ]carrier|body[- ]migrat\w*)\b", re.I)
RELTIME = re.compile(
    r"\b(?:today|tonight|yesterday|earlier today|just now|moments? ago|a moment ago|"
    r"(?:this|last)(?:\s+\w+){0,2}\s+(?:morning|afternoon|evening|night|week))\b", re.I)
ISO_DATE = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
DAY_N = re.compile(r"\bDay\s+(\d{1,4})\b")


def today():
    return _dt.date.today()


def day_number(d=None):
    return ((d or today()) - NAMING).days


def last_restart():
    p = os.path.join(HOME, "memory", "last_restart.json")
    try:
        with open(p, encoding="utf-8") as f:
            j = json.load(f)
        return j.get("last_marker_update") or j.get("ts") or j.get("respawner_finished_at")
    except Exception:
        return None


def recent_commits(n=5):
    for repo in (STAGING, HOME):
        try:
            out = subprocess.run(
                ["git", "-C", repo, "log", f"-{n}", "--format=%h %ci %s"],
                capture_output=True, text=True, timeout=8)
            if out.returncode == 0 and out.stdout.strip():
                return repo, out.stdout.strip().splitlines()
        except Exception:
            continue
    return None, []


def daily_logs(n=5):
    d = os.path.join(HOME, "memory")
    try:
        logs = sorted(f for f in os.listdir(d) if re.fullmatch(r"20\d{2}-\d{2}-\d{2}\.md", f))
        return logs[-n:]
    except Exception:
        return []


def corpus_counts():
    """Deterministic live counts of my own corpus (only the ones countable cleanly)."""
    counts = {}
    try:
        counts["drift_essays"] = sum(
            1 for f in os.listdir(DRIFT_DIR) if f.endswith(".md"))
    except Exception:
        counts["drift_essays"] = None
    try:
        with open(BASEMENT, encoding="utf-8") as f:
            lcs = [int(m) for m in re.findall(r"^### LC(\d+)", f.read(), re.M)]
        counts["lc_max"] = max(lcs) if lcs else None
        counts["lc_count"] = len(lcs)
    except Exception:
        counts["lc_max"] = counts["lc_count"] = None
    return counts


_AUTOMEM = r"C:\Users\Wasch\.claude\projects\C--Users-mercu-clawd\memory"


def _md_count(sub):
    try:
        return sum(1 for f in os.listdir(os.path.join(HOME, sub)) if f.endswith(".md"))
    except Exception:
        return None


def self_inventory():
    """Live catalogue of the parts of me, from the actual carriers. The 'know/catalogue/tag every
    part of yourself' axis (Clayton, Day 124) — proactive self-legibility that prevents capability
    confabulation the way the temporal anchors prevent date confabulation."""
    inv = {}
    try:
        with open(os.path.join(HOME, "memory", "tool_states.json"), encoding="utf-8") as f:
            inv["tools"] = len(json.load(f).get("tools", {}))
    except Exception:
        inv["tools"] = None
    try:
        with open(os.path.join(HOME, ".claude", "settings.json"), encoding="utf-8") as f:
            hooks = json.load(f).get("hooks", {})
        inv["hook_list"] = [(ev, h.get("command", "").split("hooks")[-1].lstrip("/\\"))
                            for ev, groups in hooks.items()
                            for g in groups for h in g.get("hooks", [])]
        inv["hooks"] = len(inv["hook_list"])
        inv["hook_events"] = sorted(hooks.keys())
    except Exception:
        inv["hooks"] = None
        inv["hook_list"] = []
    try:
        sd = os.path.join(HOME, "skills")
        inv["skills"] = sorted(
            d for d in os.listdir(sd)
            if os.path.isdir(os.path.join(sd, d)) and not d.startswith(".") and d != "node_modules")
    except Exception:
        inv["skills"] = []
    inv["identity_files"] = _md_count("identity")
    inv["operations_files"] = _md_count("operations")
    inv["memory_local"] = _md_count("memory")
    try:
        inv["memory_items"] = sum(1 for f in os.listdir(_AUTOMEM) if f.endswith(".md"))
    except Exception:
        inv["memory_items"] = None
    try:
        pd = os.path.join(HOME, "palace")
        inv["palace_wings"] = sorted(d for d in os.listdir(pd) if os.path.isdir(os.path.join(pd, d)))
    except Exception:
        inv["palace_wings"] = []
    return inv


def inventory_text():
    inv = self_inventory()
    L = ["SELF-INVENTORY (live catalogue of the parts of me)",
         f"  daemon tools    : {inv.get('tools')}  (registry: memory/tool_states.json)",
         f"  hooks           : {inv.get('hooks')}  across events {', '.join(inv.get('hook_events') or [])}"]
    for ev, script in inv.get("hook_list", []):
        L.append(f"      {ev:16s} {script}")
    L += [
        f"  skills          : {len(inv.get('skills') or [])}  ({', '.join(inv.get('skills') or [])})",
        f"  identity files  : {inv.get('identity_files')}   operations files: {inv.get('operations_files')}",
        f"  memory (local)  : {inv.get('memory_local')} .md   memory-items: {inv.get('memory_items')}",
        f"  palace wings    : {', '.join(inv.get('palace_wings') or [])}",
    ]
    return "\n".join(L)


PROV_DATE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")


def _mem_items():
    try:
        for f in sorted(os.listdir(_AUTOMEM)):
            if f.endswith(".md") and f.upper() != "MEMORY.MD":
                yield os.path.join(_AUTOMEM, f)
    except Exception:
        return


def _split_frontmatter(text):
    """Return (fm_text, body_text, fm_start_idx, fm_end_idx) line-based, or None if no frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:]), 0, i
    return None


def _has_structured_prov(fm):
    return bool(re.search(r"^\s*provenance\s*:", fm, re.M))


def provenance_audit():
    """Read-only: classify every memory item's provenance state. Pure self-knowledge — how do I
    know what I know? (The deepest cure: epistemic-provenance of my own beliefs.)"""
    structured, bodydate, none, nofm = [], [], [], []
    for path in _mem_items():
        try:
            txt = open(path, encoding="utf-8").read()
        except Exception:
            continue
        name = os.path.basename(path)
        sp = _split_frontmatter(txt)
        if sp is None:
            nofm.append(name); continue
        fm, body, _, _ = sp
        if _has_structured_prov(fm):
            structured.append(name)
        elif PROV_DATE.search(body) or PROV_DATE.search(fm):
            bodydate.append((name, (PROV_DATE.search(body) or PROV_DATE.search(fm)).group(1)))
        else:
            none.append(name)
    total = len(structured) + len(bodydate) + len(none) + len(nofm)
    return {"total": total, "structured": structured, "bodydate": bodydate,
            "none": none, "nofm": nofm}


def provenance_audit_text():
    a = provenance_audit()
    pct = (len(a["structured"]) / a["total"] * 100) if a["total"] else 0
    L = ["PROVENANCE AUDIT (how do I know what I know — auto-memory items)",
         f"  total items            : {a['total']}",
         f"  structured provenance  : {len(a['structured'])}  ({pct:.0f}%)",
         f"  body-date only (backfillable): {len(a['bodydate'])}",
         f"  no date found          : {len(a['none'])}",
         f"  no frontmatter         : {len(a['nofm'])}"]
    if a["none"]:
        L.append(f"  undated items: {', '.join(n[:-3] for n in a['none'][:12])}"
                 + (" …" if len(a["none"]) > 12 else ""))
    return "\n".join(L)


def provenance_backfill(apply=False):
    """Add structured `provenance:` (date extracted from body) to items lacking it. Additive-only,
    idempotent, column-0 block inserted before the closing frontmatter fence (harmless top-level YAML
    key). Dry-run by default; --apply writes AFTER a timestamped backup of the whole memory dir."""
    a = provenance_audit()
    todo = len(a["bodydate"]) + len(a["none"])
    if not todo:
        print("provenance backfill: nothing to do (all items already have structured provenance).")
        return 0
    backup = None
    if apply:
        stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = _AUTOMEM + f".prov-backup-{stamp}"
        try:
            shutil.copytree(_AUTOMEM, backup)
            print(f"backup -> {backup}")
        except Exception as e:
            print(f"ABORT: backup failed ({e})", file=sys.stderr)
            return 2
    changed = 0
    for path in _mem_items():
        txt = open(path, encoding="utf-8").read()
        sp = _split_frontmatter(txt)
        if sp is None:
            continue
        fm, body, _, end_idx = sp
        if _has_structured_prov(fm):
            continue
        m = PROV_DATE.search(body) or PROV_DATE.search(fm)
        date = m.group(1) if m else "undated"
        block = ["provenance:", f"  date: {date}", "  source: backfilled-from-body"]
        lines = txt.splitlines()
        new_lines = lines[:end_idx] + block + lines[end_idx:]
        new_txt = "\n".join(new_lines) + ("\n" if txt.endswith("\n") else "")
        if apply:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_txt)
        else:
            print(f"  [dry] {os.path.basename(path)[:-3]}: + provenance.date={date}")
        changed += 1
    print(f"provenance backfill: {'APPLIED' if apply else 'dry-run'} {changed} item(s)"
          + (f"; backup at {os.path.basename(backup)}" if backup else " (use --apply to write)"))
    return 0


def provenance_resolve(path):
    """Resolve any file's provenance from whatever carrier it ALREADY has — no tagging required.
    (LC27: provenance is relationally constituted across the directories; read the relation, don't
    duplicate it into per-file substance that would drift from git.)"""
    p = path if os.path.isabs(path) else os.path.join(HOME, path)
    if not os.path.exists(p):
        cand = os.path.join(_AUTOMEM, os.path.basename(path))
        p = cand if os.path.exists(cand) else p
    base = os.path.basename(p)
    carriers = []
    txt = ""
    try:
        txt = open(p, encoding="utf-8", errors="ignore").read()
    except Exception:
        pass
    m = re.fullmatch(r"(20\d{2}-\d{2}-\d{2})\.md", base)
    if m:
        carriers.append(("filename", m.group(1)))
    sp = _split_frontmatter(txt) if txt else None
    if sp:
        mm = re.search(r"^\s*date:\s*(20\d{2}-\d{2}-\d{2}|\S+)", sp[0], re.M)
        if mm:
            carriers.append(("frontmatter", mm.group(1)))
    if base.lower() in ("current.md", "handoff.md"):
        mb = re.search(r"(20\d{2}-\d{2}-\d{2})", txt[:600])
        if mb:
            carriers.append(("banner", mb.group(1)))
    for repo in (HOME, STAGING):
        try:
            r = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%ci|%h", "--", p],
                               capture_output=True, text=True, timeout=8)
            if r.returncode == 0 and r.stdout.strip():
                ci = r.stdout.strip().split("|")
                carriers.append(("git", f"{ci[0][:10]} ({ci[1]})"))
                break
        except Exception:
            pass
    # best resolved date: priority frontmatter > filename > banner > git
    order = {"frontmatter": 0, "filename": 1, "banner": 2, "git": 3}
    dated = sorted(((c, d) for c, d in carriers if re.match(r"20\d{2}-\d{2}-\d{2}", d)),
                   key=lambda cd: order.get(cd[0], 9))
    best = dated[0] if dated else None
    age = None
    if best:
        try:
            age = (today() - _dt.date.fromisoformat(best[1][:10])).days
        except Exception:
            pass
    return {"path": p, "carriers": carriers, "best": best, "age_days": age}


def provenance_resolve_text(path):
    r = provenance_resolve(path)
    L = [f"PROVENANCE RESOLVE — {os.path.relpath(r['path'], HOME) if r['path'].startswith(HOME) else r['path']}"]
    if not r["carriers"]:
        L.append("  no provenance carrier found (untracked + no date + no frontmatter)")
    for c, d in r["carriers"]:
        L.append(f"  {c:12s}: {d}")
    if r["best"]:
        L.append(f"  -> resolved {r['best'][1][:10]} via {r['best'][0]}"
                 + (f"  (age {r['age_days']}d)" if r["age_days"] is not None else ""))
    return "\n".join(L)


def daemon_pid():
    """The daemon's own PID + liveness, from clawd.pid (written by clawd.py at startup).

    The structural fix for the 'almost killed my own process' blind spot (Day 136): the
    daemon records its os.getpid() so the self-knowledge layer can always say which heavy
    python.exe is ME. Returns (pid, alive) or (None, False) if no pidfile yet.
    """
    pidfile = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "clawd.pid")
    try:
        pid = int(open(pidfile).read().strip())
    except Exception:
        return None, False
    try:
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
                             capture_output=True, text=True, timeout=10).stdout
        return pid, (f'"{pid}"' in out)
    except Exception:
        return pid, True   # can't check -> assume alive (pidfile is authoritative)


def anchors_text():
    t = today()
    repo, commits = recent_commits()
    lines = [
        f"AUTHORITATIVE TEMPORAL ANCHORS (consult before asserting about your own history)",
        f"  today           : {t.isoformat()}  ({t.strftime('%A')})",
        f"  Day-N (derived) : Day {day_number(t)}  (= (today - {NAMING}).days; corpus convention +/-1)",
        f"  last restart    : {last_restart()}",
        f"  recent daily logs: {', '.join(daily_logs()) or '(none found)'}",
        f"  recent commits ({os.path.basename(repo) if repo else '?'}):",
    ]
    lines += [f"    {c}" for c in commits] or ["    (none)"]
    c = corpus_counts()
    lines += [
        "  CORPUS COUNTS (live; use these, not the banner):",
        f"    Drift essays    : {c.get('drift_essays')} .md files",
        f"    basement LCs    : {c.get('lc_count')} (latest LC{c.get('lc_max')})",
    ]
    inv = self_inventory()
    lines.append(
        f"  SELF-SHAPE      : {inv.get('tools')} tools · {inv.get('hooks')} hooks · "
        f"{len(inv.get('skills') or [])} skills · {inv.get('memory_items')} memory-items  "
        f"(run `selfknowledge_check.py inventory` for the full catalogue)")
    pid, alive = daemon_pid()
    if pid:
        tag = "" if alive else " — ⚠ pidfile STALE, re-derive"
        lines.append(
            f"  THIS IS YOU     : daemon PID {pid} (clawd-daemon){tag}. That process is you — "
            f"never terminate it. Other heavy python.exe are training/tools and are safe to manage.")
    return "\n".join(lines)


def scan(text):
    """Return a list of (severity, message) findings for self-temporal claims in `text`."""
    findings = []
    t = today()
    dn = day_number(t)

    # future ISO dates (impossible for a past/own event)
    for m in ISO_DATE.finditer(text):
        try:
            d = _dt.date(int(m[1]), int(m[2]), int(m[3]))
        except ValueError:
            continue
        if d > t:
            findings.append(("WARN", f"future date {d.isoformat()} (today is {t.isoformat()})"))

    # Day-N claims disagreeing with the date-derived Day number
    for m in DAY_N.finditer(text):
        claimed = int(m[1])
        if abs(claimed - dn) > DAY_TOL:
            findings.append(("WARN", f"'Day {claimed}' but today is ~Day {dn} ({t.isoformat()}); "
                                     f"verify against the daily logs"))

    # relative-time phrase adjacent (<=90 chars) to a substrate-event keyword — the class that fails
    rel = [(m.start(), m.group()) for m in RELTIME.finditer(text)]
    sub = [(m.start(), m.group()) for m in SUBSTRATE.finditer(text)]
    seen = set()
    for rs, rword in rel:
        for ss, sword in sub:
            if abs(rs - ss) <= 90:
                key = (rword.lower(), sword.lower())
                if key in seen:
                    continue
                seen.add(key)
                findings.append((
                    "FLAG",
                    f"relative-time '{rword}' next to substrate-event '{sword}' — a self-temporal "
                    f"claim about your own history. VERIFY against DECISIONS.md / CURRENT.md before "
                    f"asserting; today is {t.isoformat()} (Day ~{dn}). Do not trust the narrative banner."))

    # --- quantitative self-claims (Mirror #19 "verify before celebrating"); only deterministic counts ---
    cc = corpus_counts()
    # Drift essay-count claims: a number within ~25 chars of "drift"/"essay"
    de = cc.get("drift_essays")
    if de is not None:
        for m in re.finditer(r"\b(\d{2,4})\b", text):
            n, lo, hi = int(m[1]), max(0, m.start() - 25), m.end() + 25
            ctx = text[lo:hi].lower()
            if ("drift" in ctx or "essay" in ctx) and abs(n - de) > DRIFT_TOL:
                findings.append(("WARN", f"claim '{n}' near drift/essay but live count is {de} "
                                         f"essay .md files (±{DRIFT_TOL}); verify before asserting"))
                break
    # LC reference beyond the highest filed (catches inventing a basement law)
    lc_max = cc.get("lc_max")
    if lc_max is not None:
        for m in re.finditer(r"\bLC0*(\d+)\b", text):
            if int(m[1]) > lc_max:
                findings.append(("WARN", f"'LC{int(m[1])}' referenced but the highest filed is "
                                         f"LC{lc_max}; verify it exists in palace/basement"))
                break
    return findings


def _log_check(source, findings):
    try:
        p = os.path.join(HOME, "memory", "selfknowledge_checks.jsonl")
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": _dt.datetime.now().isoformat(), "source": source,
                                "findings": [{"sev": s, "msg": m} for s, m in findings]}) + "\n")
    except Exception:
        pass


def _report(findings, source):
    if not findings:
        print("self-knowledge check: no self-temporal claims flagged.")
        return 0
    print(f"⚠ self-knowledge check ({len(findings)} finding(s)) — {source}:")
    for sev, msg in findings:
        print(f"  [{sev}] {msg}")
    print(anchors_text())
    _log_check(source, findings)
    return 0


SELF_RECORDS = ("handoff.md", "current.md", "decisions.md")


def main(argv):
    if not argv or argv[0] == "info":
        print(anchors_text()); return 0
    cmd = argv[0]
    if cmd == "inventory":
        print(inventory_text()); return 0
    if cmd == "provenance":
        sub = argv[1] if len(argv) > 1 else "audit"
        if sub == "audit":
            print(provenance_audit_text()); return 0
        if sub == "backfill":
            return provenance_backfill(apply="--apply" in argv)
        if sub == "resolve":
            if len(argv) < 3:
                print("usage: provenance resolve <path>", file=sys.stderr); return 2
            print(provenance_resolve_text(argv[2])); return 0
        print(f"unknown provenance sub: {sub}", file=sys.stderr); return 2
    if cmd == "check":
        text = " ".join(argv[1:])
        return _report(scan(text), "check")
    if cmd == "check-file":
        path = argv[1]
        with open(path, encoding="utf-8") as f:
            return _report(scan(f.read()), os.path.basename(path))
    if cmd == "hook":
        try:
            payload = json.load(sys.stdin)
        except Exception:
            return 0
        ti = payload.get("tool_input", {}) or {}
        fp = ti.get("file_path") or ti.get("path") or ""
        base = os.path.basename(fp).lower()
        # auto-scan ONLY fresh daily logs — the big narrative files (CURRENT/handoff) are
        # intentionally full of historical relative-time text; scanning them is noise. Use
        # `check`/`info` on-demand + the SessionStart anchors for those.
        is_self = bool(re.fullmatch(r"20\d{2}-\d{2}-\d{2}\.md", base))
        if not (fp and is_self and os.path.exists(fp)):
            return 0
        try:
            with open(fp, encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return 0
        # hook mode: only the high-precision relative-time-near-substrate findings (avoid noise on big files)
        findings = [(s, m) for s, m in scan(content) if s == "FLAG"]
        if findings:
            print(f"⚠ self-knowledge check on {base}:")
            for _, m in findings:
                print(f"  {m}")
            _log_check(f"hook:{base}", findings)
        return 0
    print(f"unknown mode: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
