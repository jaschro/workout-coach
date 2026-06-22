"""
upload_to_github.py
Uploads updated app files to the public repo and data files to the private repo.
"""
import base64, json, os, urllib.request, urllib.error, urllib.parse

TOKEN      = "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"
OWNER      = "jaschro"
CODE_REPO  = "workout-coach"
DATA_REPO  = "workout-coach-private-data"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

def api_url(repo, path):
    encoded = "/".join(urllib.parse.quote(seg, safe="") for seg in path.split("/"))
    return f"https://api.github.com/repos/{OWNER}/{repo}/contents/{encoded}"

def get_sha(repo, path):
    req = urllib.request.Request(api_url(repo, path), headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())["sha"]
    except urllib.error.HTTPError as e:
        if e.code == 404: return None
        raise

def upload(repo, repo_path, local_path, message, is_text=True):
    mode = "r" if is_text else "rb"
    enc  = "utf-8" if is_text else None
    with open(local_path, mode, encoding=enc) as f:
        raw = f.read()
    content = base64.b64encode(raw.encode("utf-8") if is_text else raw).decode()
    sha  = get_sha(repo, repo_path)
    body = {"message": message, "content": content}
    if sha: body["sha"] = sha
    req = urllib.request.Request(
        api_url(repo, repo_path),
        data=json.dumps(body).encode(),
        headers={**HEADERS, "Content-Type": "application/json"},
        method="PUT",
    )
    try:
        with urllib.request.urlopen(req):
            print(f"  ✓  [{repo}]  {repo_path}")
    except urllib.error.HTTPError as e:
        print(f"  ✗  [{repo}]  {repo_path}: {e.code} {e.read()[:120]}")

HERE = os.path.dirname(os.path.abspath(__file__))

print("Uploading files...\n")

# Public repo — app code only
upload(CODE_REPO, "index.html", os.path.join(HERE, "index.html"), "Point data at private repo")

# Private repo — data files
upload(DATA_REPO, "workout-log.json", os.path.join(HERE, "workout-log.json"), "Migrate workout log data")
upload(DATA_REPO, "workout-log.csv",  os.path.join(HERE, "workout-log.csv"),  "Migrate workout log CSV")

print("\nDone.")
print("\nIMPORTANT: Your PAT needs access to both repos.")
print("Update it at: GitHub → Settings → Developer settings →")
print("Personal access tokens → Fine-grained tokens → edit your token")
print("→ add 'workout-coach-private-data' with Contents: Read & Write")
