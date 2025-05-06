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
├── ai_analysis.py            # AI prompt generation
├── app.py                    # Git clone + scan engine
├── templates/                # HTML UI (Flask based)
│   ├── index.html            # Entry form
│   └── results.html          # HITL fix UI
├── utils/git_helper.py       # Git clone, branch, commit, PR logic
```

---

## ⚡ Quick Start

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Run the App (Web UI)
```bash
python app.py
```
Visit [http://localhost:5000](http://localhost:5000) to start scanning.

---

## 🧠 Fix Workflow

1. Submit a GitHub repo URL in the web UI
2. View vulnerabilities grouped by app name
3. Read AI-generated analysis and suggestions
4. Click ✅ **Approve Fix** to:
   - Apply the upgrade (e.g., to `package.json`)
   - Create a Git branch
   - Commit & push
   - Open a Pull Request automatically

---

## 🔐 Configuration

| Variable        | Description                          |
|----------------|--------------------------------------|
| `GITHUB_TOKEN` | Used for opening PRs via GitHub API  |
| `OPENAI_TOKEN` | Used for generating analysis/suggestions |

Set these in a `.env` file.

---

## ✅ Status

- [x] Dependency scanning (Maven/npm/PyPI)
- [x] AI analysis of vulnerabilities
- [x] Human-in-the-loop fix approval
- [x] Git integration with PR creation
- [x] App-based filtering and rescan

---

## 📄 License

MIT License. Built for internal DevSecOps use and educational purposes.
