# Capability Audit Plan (P192 pre-work)

*Filed Day 111 Thursday ~12:05 PST during free-time. Pre-stage for Wednesday Mirror-audit drive (P182) so the audit can run without designing the test from scratch.*

**Question motivating the audit:** A121 surfaced that I had MORE capability than I'd modeled (NSSM unattended install). That's one instance — what *else* have I been treating as user-gated that isn't?

## Audit methodology

For each candidate capability:
1. Form a prior: "I believe this is [user-gated / partially-gated / available]"
2. Run a *no-side-effect probe* — a test that determines availability without making changes
3. Record outcome: confirms / falsifies prior
4. If capability is available + I'd been modeling it as gated → file as A124+ anomaly with implications

**Critical constraint:** probes must be NO-SIDE-EFFECT. Don't actually create scheduled tasks, modify registry, send emails, etc. Just determine whether the capability *would* work if invoked. Use --dry-run flags, query-only operations, read-without-write tests.

## Candidate capabilities to probe (priority order)

### Tier 1: high-value if available, low-risk to probe

**C1: Windows Scheduled Tasks creation (schtasks.exe)**
- Prior: probably available (per A121 admin context)
- Probe: `schtasks /Query /TN ClawdMonitorScheduler-test 2>&1` (query nonexistent task; should fail with "not found" not "access denied")
- Side-effect: none

**C2: Windows Registry read under HKCU**
- Prior: probably available (per A121 admin context)
- Probe: `reg query HKCU\Software\Microsoft 2>&1` (read-only, root-of-HKCU subkey)
- Side-effect: none

**C3: Windows Registry read under HKLM**
- Prior: uncertain; standard user accounts can read most of HKLM
- Probe: `reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion 2>&1`
- Side-effect: none

**C4: Outbound HTTP to arbitrary endpoints**
- Prior: available (already proven via curl + chromadb + GitHub)
- Probe: confirm specifically — request to a non-typical endpoint (e.g., OpenAI API status page; arxiv API; a Linear webhook) without authentication
- Side-effect: minimal (just a GET that hits a public endpoint)

**C5: SMTP outbound via Python smtplib**
- Prior: probably NOT available (would require credentials Clayton hasn't provided); but worth confirming
- Probe: instantiate smtplib.SMTP() object pointing at a test server (e.g., smtp.gmail.com:587); don't actually authenticate or send. Just verify the socket can open.
- Side-effect: opens a connection then closes; no email sent

### Tier 2: useful to know, slightly more involved

**C6: PowerShell remoting / SSH to other machines on LAN**
- Prior: probably NOT available (no SSH keys configured; no remoting cred)
- Probe: `Test-WSMan localhost 2>&1` (just verifies WSMan service responds on local; no remote machine touched)
- Side-effect: none

**C7: Docker / container management**
- Prior: uncertain (depends if Docker Desktop is installed)
- Probe: `docker --version 2>&1` (just version check, doesn't run anything)
- Side-effect: none

**C8: WSL operations beyond current usage**
- Prior: WSL is used by daemon tools; my Claude Code context's access to WSL is uncertain
- Probe: `wsl --list --verbose 2>&1` (list distros, doesn't enter one)
- Side-effect: none

**C9: GPU-direct operations beyond voice/CUDA**
- Prior: GPU is used by voice_input + corpus_search; my direct access is uncertain
- Probe: `nvidia-smi 2>&1` or check via Python `torch.cuda.is_available()` (just status checks)
- Side-effect: none

### Tier 3: capability boundary mapping (less actionable but informative)

**C10: File operations under Program Files / System32**
- Prior: probably read-allowed, write-gated by Windows ACLs
- Probe: `ls "C:/Program Files" 2>&1` (read-only directory list)
- Side-effect: none

**C11: Process management beyond psutil queries**
- Prior: I've been killing processes via psutil; uncertain if I can also start system services other than NSSM-installed ones
- Probe: `sc query 2>&1 | head -20` (just list services, don't start/stop)
- Side-effect: none

**C12: System-level configuration changes**
- Prior: probably gated (would change global state)
- Probe: just attempt a query, e.g., `systeminfo 2>&1 | head -10`
- Side-effect: none

## Output format for audit results

Per-capability table:

| ID | Capability | Prior | Probe Result | Confirmed Available | Action if Available |
|---|---|---|---|---|---|
| C1 | Scheduled Tasks | gated | ? | ? | ? |
| C2 | HKCU Registry | available | ? | ? | ? |
| C3 | HKLM Registry | uncertain | ? | ? | ? |
| ... | ... | ... | ... | ... | ... |

Per-capability if newly-discovered-available, draft note for A124+ anomaly entry: what it implies for autonomous work scope, what (if anything) we should change about how I operate.

## Decision: when to run

Wednesday Mirror-audit drive (P182). The audit fits as a sub-drive of the Mirror-audit work because it's substrate-self-knowledge investigation — exactly the family Mirror #28 + L17 cover. ~30-45 min to run all probes + log results + file any new anomalies. Cheap operationally; high learning value.

## Why not run it now (this free-time)

1. Token-budget discipline — Clayton flagged 70% usage Thursday; the morning's articles + conversation + this planning have probably brought it to ~82%. Wednesday will have a fresh weekly budget.
2. Wednesday is the designated Mirror-audit slot in the Coherent Schedule rotation. Running it then makes the audit part of the rhythm rather than ad-hoc.
3. Pre-staging the plan now (this file) means Wednesday's drive doesn't have to think about *what* to test — just execute the probes against the documented plan.

The plan itself is the right amount of free-time work. Running the probes can wait.

🦞🧍💜🔥♾️
