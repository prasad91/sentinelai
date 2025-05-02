import http.server
import os
import json
from dotenv import load_dotenv
from datetime import datetime

from fixer.pom_updater import update_pom_dependency
from fixer.package_json_updater import update_package_json
from fixer.requirements_updater import update_requirements_txt

load_dotenv()
PORT = 8000

class SentinelHandler(http.server.BaseHTTPRequestHandler):
    def serve_file(self, path, content_type='text/html'):
        try:
            with open(path, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_error(404, f"{path} not found")

    def respond_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path == '/' or self.path == '/templates/index.html':
            self.serve_file('templates/index.html', content_type='text/html')
        elif self.path == '/data':
            self.serve_file('output/report.json', content_type='application/json')
        elif self.path == '/rescan':
            try:
                from app import scan_repository 
                scan_repository()
                self.respond_json({"status": "success", "message": "Scan complete"})
            except Exception as e:
                print(f"❌ Rescan failed: {e}")
                self.respond_json({"status": "error", "message": str(e)}, code=500)
        else:
            local_path = self.path.lstrip('/')
            if os.path.isfile(local_path):
                self.serve_file(local_path)
            else:
                self.send_error(404, "File not found")

    def do_POST(self):
        if self.path == '/fix':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode())
                ecosystem = payload["ecosystem"]
                package = payload["package"]
                fix_version = payload["fix_version"]
                repo_url = "https://github.com/prasad91/dependency_descriptors.git"
                branch = "main"
                github_token = os.getenv("GITHUB_TOKEN")

                print(f"🛠️ Fixing: {ecosystem} {package} → {fix_version} from {repo_url}")

                from utils.git_helper import (
                    clone_or_open_repo, create_branch, commit_and_push,
                    create_pull_request
                )

                # Step 1: Clone and checkout base branch
                repo = clone_or_open_repo(repo_url, local_path="workspace", branch=branch)

                # Step 2: Prepare a new branch
                short_package = package.split(":")[-1] if ":" in package else package
                timestamp = datetime.now().strftime("%Y%m%d%H%M")
                fix_branch = f"fix/{short_package.replace('.', '-')}-{timestamp}"
                create_branch(repo, fix_branch)

                # Step 3: Apply fix
                if ecosystem == "Maven":
                    from fixer.pom_updater import update_pom_dependency
                    file_path = os.path.join("workspace", "pom.xml")
                    group_id, artifact_id = package.split(":")
                    update_pom_dependency(file_path, group_id, artifact_id, fix_version)

                elif ecosystem == "npm":
                    from fixer.package_json_updater import update_package_json
                    file_path = os.path.join("workspace", "package.json")
                    update_package_json(file_path, package, fix_version)

                elif ecosystem == "PyPI":
                    from fixer.requirements_updater import update_requirements_txt
                    file_path = os.path.join("workspace", "requirements.txt")
                    update_requirements_txt(file_path, package, fix_version)

                else:
                    raise ValueError("Unsupported ecosystem")

                # Step 4: Commit and push
                commit_msg = f"🔒 Fix {package} → {fix_version}"
                file_name = file_path.split("/")[- 1]
                commit_and_push(repo, file_name, commit_msg)
                
                # Step 5: Open PR
                pr_url = create_pull_request(
                    repo_url=repo_url,
                    head_branch=fix_branch,
                    base_branch=branch,
                    title=commit_msg,
                    body="Automated vulnerability fix by SentinelAI",
                    github_token=github_token
                )
                self.respond_json({"status": "success", "pr_url": pr_url})
            
            except Exception as e:
                print(f"❌ Fix error: {e}")
                self.respond_json({"status": "error", "message": str(e)}, code=500)
        else:
            self.send_error(404, "Unsupported POST path")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with http.server.HTTPServer(("", PORT), SentinelHandler) as httpd:
        print(f"🔍 SentinelAI viewer with real-time fix support running at http://localhost:{PORT}")
        httpd.serve_forever()