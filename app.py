from scanner.pom_parser import parse_pom
from scanner.package_json_parser import parse_package_json
from scanner.requirements_parser import parse_requirements
from scanner.osv_client import query_osv
from scanner.report_generator import generate_report
from ai_analysis import generate_analysis

import os

from utils.git_helper import clone_or_open_repo

def _generate_ai_analysis(vulns):
    results = []
    for vuln in vulns:
        ai_summary = generate_analysis({
            "id": vuln.get("id"),
            "summary": vuln.get("summary"),
            "package": vuln.get("package"),
            "version": vuln.get("version")
        })
        if ai_summary:
            vuln["ai_analysis"] = ai_summary
        results.append(vuln)
    return results

def scan_dependencies(repo_url, branch, repo_path, output_path):
    if os.path.exists(output_path):
        os.remove(output_path)

    print(f" Cloning {repo_url} (branch: {branch})")
    clone_or_open_repo(repo_url, repo_path, branch)

    results = []

    print(" Scanning for dependencies...")

    pom_file = os.path.join(repo_path, "pom.xml")
    if os.path.exists(pom_file):
        deps = parse_pom(pom_file)
        results.extend(_scan_dependencies(deps, "Maven"))

    pkg_json = os.path.join(repo_path, "package.json")
    if os.path.exists(pkg_json):
        deps = parse_package_json(pkg_json)
        results.extend(_scan_dependencies(deps, "npm"))

    reqs = os.path.join(repo_path, "requirements.txt")
    if os.path.exists(reqs):
        deps = parse_requirements(reqs)
        results.extend(_scan_dependencies(deps, "PyPI"))

    print(f" Writing report to {output_path}")
    generate_report(results, output_path, append=False)
    print(" Scan complete.")

def _scan_dependencies(dependencies, ecosystem):
    results = []

    for dep in dependencies:
        vulns = query_osv(dep["package"], dep["version"], ecosystem)
        vulns = _generate_ai_analysis(vulns)

        if vulns:
            results.append({
                **dep,
                "app": dep["app"],
                "type": "dependency",
                "ecosystem": ecosystem,
                "package": dep["package"],
                "version": dep["version"],
                "vulnerabilities": vulns
            })

    return results

def scan_repository():
    repo_url = "https://github.com/prasad91/dependency_descriptors.git"
    branch = "main"
    repo_path = "workspace"
    output_path = "output/report.json"
    scan_dependencies(repo_url, branch, repo_path, output_path)

if __name__ == "__main__":
    scan_repository()