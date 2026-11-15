import sys, zipfile, io, urllib.request

token_line = open(r"C:/Users/Admin/.git-credentials").read()
import re
m = re.search(r"gho_[a-zA-Z0-9]+", token_line)
token = m.group(0)

artifacts_url = "https://api.github.com/repos/keizenx/ctf-avx512-dump/actions/artifacts"
req = urllib.request.Request(artifacts_url, headers={"Authorization": f"token {token}"})
d = __import__("json").load(urllib.request.urlopen(req))
outdir = sys.argv[1] if len(sys.argv) > 1 else "."
for a in d.get("artifacts", []):
    if a["status"] != "completed":
        continue
    url = a["archive_download_url"]
    req = urllib.request.Request(url, headers={"Authorization": f"token {token}"})
    print("telecharge:", a["name"], a["size_in_bytes"], "octets")
    resp = urllib.request.urlopen(req)
    z = zipfile.ZipFile(io.BytesIO(resp.read()))
    z.extractall(outdir)
    for n in z.namelist():
        print("  extrait:", n)
