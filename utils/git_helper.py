import os
from git import Repo, GitCommandError
import requests

def clone_or_open_repo(repo_url, local_path="workspace", branch="main"):
    if os.path.exists(local_path) and os.path.isdir(os.path.join(local_path, ".git")):
        repo = Repo(local_path)
        repo.git.checkout(branch)
        repo.remotes.origin.pull()
    else:
        repo = Repo.clone_from(repo_url, local_path, branch=branch)
    return repo

def create_branch(repo, new_branch):
    try:
        if new_branch in repo.heads:
            print(f"🧹 Deleting stale local branch: {new_branch}")
            repo.git.branch("-D", new_branch)
        
        repo.git.checkout("main")
        repo.remotes.origin.pull()
        repo.git.checkout("-b", new_branch)
        print(f"✅ Created and checked out branch: {new_branch}")
    except GitCommandError as e:
        print(f"❌ Branch checkout/create error: {e}")

def commit_and_push(repo, file_path, message):
    repo.index.add([file_path])
    repo.index.commit(message)
    origin = repo.remote(name="origin")
    origin.push(refspec=f"{repo.active_branch.name}:{repo.active_branch.name}")

    print(f"📤 Pushed fix to branch: {repo.active_branch.name}")

def push_branch(repo, branch_name):
    try:
        origin = repo.remote(name="origin")
        origin.push(branch_name)
    except GitCommandError as e:
        print(f"❌ Push failed: {e}")

def create_pull_request(repo_url, head_branch, base_branch, title, body, github_token):
    """
    repo_url should be: https://github.com/owner/repo.git
    """
    parts = repo_url.rstrip(".git").split("/")
    owner = parts[-2]
    repo = parts[-1]

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "title": title,
        "head": head_branch,
        "base": base_branch,
        "body": body
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        pr_url = response.json().get("html_url")
        print(f"✅ Pull request created: {pr_url}")
        return pr_url
    else:
        print(f"❌ Failed to create PR: {response.status_code}, {response.text}")
        return None
