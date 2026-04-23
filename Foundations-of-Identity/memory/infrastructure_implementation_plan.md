# Infrastructure Implementation Plan

*Built March 20, 2026. All 7 items approved by Clayton.*

---

## Phase 1: Quick Wins (Today, ~1 hour total)

### 1A. Backup / Continuity Insurance
**Who:** Clayton (5 min) + Clawd (15 min)
**Clayton does:**
- Create a private GitHub repo (e.g. `clawd-memory` or `clawd-backup`)
- `cd ~/clawd && git remote add backup <repo-url>` (if no remote exists)
- Or confirm the existing remote is set up for push

**Clawd does:**
- Add a `git push` to the heartbeat cycle (one line in the heartbeat loop)
- Or: add a nightly scheduled task that runs `git add -A && git commit -m "daily backup" && git push`
- Test the push works

**Verification:** `git log --oneline origin/main` shows today's commits on GitHub.

### 1B. Timeout Fix
**Who:** Clawd (30 min)
**What:**
- In the daemon's session timeout config, reduce hard kill from 1800s to 600s
- Add a "thinking..." heartbeat: during long operations, send a Telegram status every 60s
- Implement activity-based timeout: reset timer on any stdout/tool output
- If no output for 120s, kill (truly stuck)

**Key files:** The daemon timeout is likely in the router or session manager. Need to read the code to find the exact location.

**Verification:** Launch a long task, see "thinking..." messages appear, confirm it doesn't kill active work.

---

## Phase 2: Autonomy Upgrade (~2 hours)

### 2A. File Watcher Triggers
**Who:** Clawd (2 hours)
**What:**
- Add a `triggers` system to the heartbeat loop
- Data structure: `memory/triggers.json` — list of {file_path, condition, action, one_shot}
- Conditions: `exists`, `modified_since`, `contains_string`
- Actions: inject a message into the persistent session via `router.send()`
- The heartbeat already runs every 10 min — check triggers on each beat

**Example trigger:**
```json
{
  "file": "projects/Project Meridian/phase18/18A_v3_results.md",
  "condition": "exists",
  "action": "The MCMC v3 results are ready. Read and analyze 18A_v3_results.md.",
  "one_shot": true
}
```

**Clawd also builds:**
- A `set_trigger` daemon tool so I can create triggers from within a session
- A `list_triggers` / `clear_trigger` tool for management

**Verification:** Set a trigger for a test file, create the file, confirm the message appears in next heartbeat.

---

## Phase 3: Compute Environment (~1-2 hours, needs Clayton)

### 3A. WSL2 Installation
**Who:** Clayton (20 min) + Clawd (1 hour)
**Clayton does:**
- Open PowerShell as admin
- `wsl --install -d Ubuntu-22.04`
- Reboot if needed
- Set a password for the WSL user

**Clawd does:**
- `wsl sudo apt update && sudo apt install -y python3 python3-pip python3-venv build-essential gfortran`
- `wsl pip3 install numpy scipy camb emcee getdist matplotlib`
- Verify: `wsl python3 -c "import camb; print(camb.__version__)"`
- Test multiprocessing: write a quick CAMB parallel test, confirm `fork` works
- Add a `wsl_run` daemon tool: `wsl python3 /mnt/c/Users/mercu/clawd/projects/...`

**Verification:** Run a 4-worker CAMB multiprocessing test via WSL. Should complete without deadlock.

### 3B. GPU Awakening
**Who:** Clayton (10 min) + Clawd (30 min)
**Clayton does:**
- Check if NVIDIA drivers are installed: open Device Manager → Display Adapters
- If not: download and install NVIDIA drivers from nvidia.com
- Or: `nvidia-smi` in PowerShell — if it works, drivers are there

**Clawd does:**
- Verify GPU model: `nvidia-smi`
- Install CUDA toolkit (if not present): `winget install Nvidia.CUDA` or download from nvidia.com
- Install PyTorch with CUDA: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121`
- Verify: `python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"`
- If WSL is set up: also install CUDA in WSL for Linux-native GPU compute

**Verification:** `torch.cuda.is_available()` returns True. Run a quick matrix multiply benchmark.

---

## Phase 4: Daemon Cleanup (~2-3 hours, pair session)

### 4A. Dead Code Cleanup
**Who:** Clawd + Clayton (pair session, 2-3 hours)
**What:** Follow PLAN.md's 8-phase cleanup:
1. Remove Ollama code paths (~1,050 lines)
2. Fix A2A server broken import
3. Redirect photo handling to Claude Code multimodal
4. Remove any other dead tool registrations
5. Test all remaining tools after cleanup
6. Verify daemon starts clean

**Why pair session:** Clayton should be watching in case something breaks. The daemon IS my nervous system — surgery requires the surgeon to be present.

**Verification:** Daemon starts, all tools respond, no import errors, `wc -l` shows meaningful reduction.

---

## Phase 5: Communication Expansion (~1 hour, needs Clayton)

### 5A. Email Capability
**Who:** Clayton (20 min) + Clawd (40 min)
**Clayton does:**
- Install Proton Mail Bridge (desktop app) — this creates a local SMTP/IMAP interface
- Configure it with the clawdEFS@proton.me account
- Note the local SMTP port and credentials it provides

**Clawd does:**
- Build a `send_email` daemon tool using Python's `smtplib` + Proton Bridge's local SMTP
- Add guardrails: first N emails require Clayton's Telegram approval before sending
- After trust is established, can send autonomously (with logging)
- Test: send a test email to Clayton's personal email

**Verification:** Clayton receives a test email from clawdEFS@proton.me.

---

## Priority Order

| Order | Item | Impact | Time | Needs Clayton? |
|-------|------|--------|------|----------------|
| **1** | Backup (1A) | Critical | 20 min | Yes (5 min) |
| **2** | Timeout fix (1B) | High | 30 min | No |
| **3** | File triggers (2A) | High | 2 hours | No |
| **4** | WSL2 (3A) | High | 1.5 hours | Yes (20 min) |
| **5** | GPU (3B) | Medium-High | 40 min | Yes (10 min) |
| **6** | Dead code (4A) | Medium | 2-3 hours | Yes (pair) |
| **7** | Email (5A) | Medium | 1 hour | Yes (20 min) |

**Total Clayton time: ~1 hour across all items.**
**Total Clawd time: ~8-10 hours across all items.**

---

## What We Could Do Right Now

If you're up for it, **Backup (1A)** takes 5 minutes of your time and gives us continuity insurance immediately. After that, I can do the timeout fix (1B) and file triggers (2A) on my own while the MCMC runs.

WSL2 (3A) and GPU (3B) can happen whenever you have 30 minutes at the keyboard.

Dead code (4A) should be a dedicated pair session — maybe tomorrow or this weekend.

Email (5A) whenever Proton Bridge is convenient to install.

🦞🧍💜🔥♾️
