from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
import tempfile
import re
import shutil
import git
from dotenv import load_dotenv
from scanner.pom_parser import parse_pom
from scanner.package_json_parser import parse_package_json
from scanner.requirements_parser import parse_requirements
from scanner.osv_client import check_vulnerabilities, query_osv
from fixer.pom_updater import update_pom
from fixer.requirements_updater import update_requirements
from fixer.package_json_updater import update_package_json
from utils.git_helper import clone_or_open_repo, create_branch, commit_and_push, create_pull_request
from ai_analysis import generate_analysis

load_dotenv()

app = Flask(__name__)

OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey123")
BRANCH_NAME = "main"

vulns_store = []

def clone_repo(repo_url):
    temp_dir = tempfile.mkdtemp()
    git.Repo.clone_from(repo_url, temp_dir)
    return temp_dir

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        repo_url = request.form['repo_url']
        try:
            repo_path = clone_repo(repo_url)
            dependencies = scan_dependencies(repo_path)
            vulns = []

            for dep in dependencies:
                results = check_vulnerabilities(dep)
                for r in results:
                    if r.get("affected"):
                        vuln_info = {
                            "app": dep["app"],
                            "file": dep.get("file"),
                            "package": dep["package"],
                            "version": dep["version"],
                            "id": r["id"],
                            "summary": r.get("summary", "No summary")
                        }
                        analysis = generate_analysis(vuln_info)
                        vuln_info.update(analysis)
                        vulns.append(vuln_info)

            shutil.rmtree(repo_path)

            if not vulns:
                flash("No vulnerabilities found!", "info")
                return redirect(url_for('index'))

            apps = list(set([v["app"] for v in vulns]))
            return render_template('results.html', vulns=vulns, apps=apps, selected_app="All")

        except Exception as e:
            flash(f"Error scanning repository: {str(e)}", "danger")
            return redirect(url_for('index'))

    return render_template('index.html')

def scan_pom_dependencies(repo_path):
    file_name="pom.xml"
    pom_path = os.path.join(repo_path, file_name)
    if os.path.exists(pom_path):
        deps = parse_pom(pom_path)
        for d in deps:
            d["file"] = file_name
        return deps
    return []

def scan_package_json_dependencies(repo_path):
    file_name="package.json"
    pkg_path = os.path.join(repo_path, file_name)
    if os.path.exists(pkg_path):
        deps = parse_package_json(pkg_path)
        for d in deps:
            d["file"] = file_name
        return deps
    return []

def scan_requirements_dependencies(repo_path):
    file_name="requirements.txt"
    req_path = os.path.join(repo_path, file_name)
    if os.path.exists(req_path):
        deps = parse_requirements(req_path)
        for d in deps:
            d["file"] = file_name
        return deps
    return []

def scan_dependencies(repo_path):
    all_deps = []
    all_deps.extend(scan_pom_dependencies(repo_path))
    all_deps.extend(scan_package_json_dependencies(repo_path))
    all_deps.extend(scan_requirements_dependencies(repo_path))
    return all_deps

@app.route("/scan", methods=["POST"])
def scan():
    global vulns_store
    repo_url = request.form.get("repo_url")
    repo_path = tempfile.mkdtemp()
    clone_or_open_repo(repo_url, repo_path, branch=BRANCH_NAME)

    vulns_store = []

    deps = scan_dependencies(repo_path)
    for dep in deps:
        results = query_osv(ecosystem=dep["ecosystem"], package=dep["package"], version=dep["version"])
        for r in results:
            if all(k in r for k in ["id", "package", "version", "fix_version"]):
                vuln_info = {
                    "app": dep["app"],
                    "file": dep.get("file"),
                    "package": dep["package"],
                    "version": dep["version"],
                    "id": r["id"],
                    "summary": r.get("summary", "No summary"),
                    "fix_version": r["fix_version"]
                }
                analysis = generate_analysis(vuln_info)
                vuln_info.update(analysis)
                vulns_store.append(vuln_info)

    apps = sorted(set(v["app"] for v in vulns_store))
    
    if not apps:
        flash("No vulnerabilities found!", "info")
        return redirect(url_for("index"))

    return render_template("results.html", vulns=vulns_store, apps=apps, selected_app="All")

@app.route("/approve", methods=["POST"])
def approve():
    data = request.json
    v = next((item for item in vulns_store if item["id"] == data["id"] and item["package"] == data["package"]), None)
    if not v:
        return jsonify({"error": "Vulnerability not found"}), 404

    repo_url = data.get("repo_url")
    repo_path = tempfile.mkdtemp()
    repo = clone_or_open_repo(repo_url, repo_path, branch=BRANCH_NAME)
    safe_package = re.sub(r'[^a-zA-Z0-9_-]', '-', v['package'])
    safe_id = re.sub(r'[^a-zA-Z0-9_-]', '-', v['id'].lower())
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    branch = f"sentinelai-fix-{safe_package}-{safe_id}-{timestamp}"

    create_branch(repo, branch)
    filepath = os.path.join(repo_path, v["file"])

    if v['file'] == "pom.xml":
        update_pom(filepath, v['package'].split(":")[0], v['package'].split(":")[1], v['fix_version'])
    elif v['file'] == "requirements.txt":
        update_requirements(filepath, v['package'], v['fix_version'])
    elif v['file'] == "package.json":
        update_package_json(filepath, v['package'], v['fix_version'])

    commit_and_push(repo, filepath, f"fix: {v['id']} in {v['package']}")

    pr_url = create_pull_request(
        repo_url=repo_url,
        head_branch=branch,
        base_branch=BRANCH_NAME,
        title=f"Fix {v['id']} - {v['package']}",
        body=f"**Issue:** {v['summary']}\n\n**Impact:** {v['impact']}\n\n**Fix:** {v['suggestion']}",
        github_token=GITHUB_TOKEN
    )

    return jsonify({"pr_url": pr_url or "PR creation failed"})

if __name__ == "__main__":
    app.run(debug=True)
