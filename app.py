from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import tempfile
import re
from dotenv import load_dotenv
from scanner.pom_parser import parse_pom
from scanner.package_json_parser import parse_package_json
from scanner.requirements_parser import parse_requirements
from scanner.osv_client import query_osv
from fixer.pom_updater import update_pom
from fixer.requirements_updater import update_requirements
from fixer.package_json_updater import update_package_json
from utils.git_helper import clone_or_open_repo, create_branch, commit_and_push, create_pull_request
from ai_analysis import generate_analysis

load_dotenv()

app = Flask(__name__)

OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BRANCH_NAME = "main"

vulns_store = []

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def scan():
    global vulns_store
    repo_url = request.form.get("repo_url")
    repo_path = tempfile.mkdtemp()
    clone_or_open_repo(repo_url, repo_path, branch=BRANCH_NAME)

    vulns_store = []

    for parser, filename in [(parse_pom, "pom.xml"), (parse_package_json, "package.json"), (parse_requirements, "requirements.txt")]:
        filepath = os.path.join(repo_path, filename)
        if os.path.exists(filepath):
            deps = parser(filepath)
            for dep in deps:
                results = query_osv(ecosystem=dep["ecosystem"], package=dep["package"], version=dep["version"])
                for r in results:
                    if all(k in r for k in ["id", "package", "version", "fix_version"]):
                        vuln_info = {
                            "app": dep.get("app", filename),
                            "file": filename,
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
    branch = f"sentinelai-fix-{safe_package}-{safe_id}"

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
