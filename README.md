
# 🛡️ SentinelAI

**SentinelAI** is a lightweight, agent-assisted security tool that scans open source dependencies for known vulnerabilities using [OSV.dev](https://osv.dev), explains issues using AI, and allows human-in-the-loop (HITL) approvals to apply real-time fixes and auto-create GitHub pull requests.

---

## 🚀 Features

- 🔍 Detects vulnerable dependencies in:
  - `pom.xml` (Maven)
  - `package.json` (npm)
  - `requirements.txt` (PyPI)
- 🤖 AI-assisted analysis for each vulnerability
- ✅ Human-in-the-loop review:
  - “Fix Now” applies live fixes
  - “Fix Later” defers action
- ⚙️ Real-time file updates via local or remote Git
- 🌿 Git integration:
  - Creates fix branches
  - Commits patched files
  - Opens Pull Requests
- 🔄 Rescan button to re-pull, scan, and refresh the UI

---

## 📂 Project Structure

```
SentinelAI/
├── scanner/                  # Dependency parsers + fix modules
│   ├── pom_parser.py         # Maven
│   ├── package_json_parser.py
│   ├── requirements_parser.py
│   ├── osv_client.py         # Talks to OSV.dev
│   ├── pom_updater.py        # Fix logic
├── viewer.py                 # Web UI server with HITL controls
├── app.py                    # Git clone + auto-scan CLI
├── git_helper.py             # Git clone, branch, commit, PR
├── output/report.json        # Scan result with AI analysis
├── templates/index.html      # Frontend UI
```

---

## ⚡ Quick Start

### 1. Install Requirements

```bash
pip install -r requirements.txt
```

### 2. Run the Scanner (from Git)

```bash
python app.py
```

This clones the repo, scans dependencies, and generates `report.json`.

### 3. Start the Viewer

```bash
python viewer.py
```

Visit [http://localhost:8000](http://localhost:8000) to review results.

---

## 🧠 Fix Workflow

1. Review vulnerabilities in the UI
2. Click ✅ **Fix Now** to:
   - Apply the upgrade (e.g., to `pom.xml`)
   - Create a Git branch
   - Commit & push
   - Open a Pull Request automatically

---

## 🔐 Configuration

| Variable        | Description                          |
|----------------|--------------------------------------|
| `GITHUB_TOKEN` | Used for opening PRs via GitHub API  |
| `repo_url`     | Git repo to scan and patch           |
| `branch`       | Base branch (default: `main`)        |

---

## ✅ Status

- [x] Dependency scanning (Maven/npm/PyPI)
- [x] AI analysis of vulnerabilities
- [x] Human-in-the-loop fix approval
- [x] Git integration with PR creation
- [x] Real-time UI and Rescan

---

## 📄 License

MIT License. Built for educational and internal DevSecOps automation.
