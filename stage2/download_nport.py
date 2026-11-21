"""
download_nport.py: fetch the SEC "Form N-PORT Data Sets" (fund holdings, 2019Q4 onward).

Stage 2 of the pivot (docs/stage2/FEASIBILITY.md): fund-level holdings with share
counts (BALANCE, unit NS) and series IDs, for fund horizons and manager shocks.

The SEC requires a User-Agent with a real contact. Set your own once:
    export SEC_CONTACT_EMAIL="you@example.com"     (e.g. in ~/.zshrc)
The script refuses to run without it.

Usage (from the repo root):
    python stage2/download_nport.py              # download every data set (about 11 GB)
    python stage2/download_nport.py --only 2023q1  # one quarter
Files land in nport_cache/ (gitignored) with nport_cache/manifest.json
recording URL, size and sha256 for each zip. Re-running skips complete files.
Polite: one request at a time, a pause between requests (SEC fair-access
policy allows at most 10 requests per second; we stay far below).
"""
import argparse, hashlib, json, os, re, sys, time
from pathlib import Path
from urllib.parse import urljoin
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "nport_cache"
INDEX_URL = "https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets"
PAUSE_S = 1.0

def session():
    contact = os.environ.get("SEC_CONTACT_EMAIL", "").strip()
    if not contact or "@" not in contact:
        sys.exit("SEC_CONTACT_EMAIL is not set. Run: export SEC_CONTACT_EMAIL=\"you@example.com\"")
    s = requests.Session()
    s.headers.update({"User-Agent": "CME-Validation " + contact, "Accept-Encoding": "gzip, deflate"})
    return s

def list_zips(s):
    r = s.get(INDEX_URL, timeout=60)
    r.raise_for_status()
    links = sorted(set(re.findall(r'href="([^"]+_nport\.zip)"', r.text, flags=re.I)))
    return [urljoin(INDEX_URL, l) for l in links]

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only", nargs="*", help="quarters such as 2023q1")
    args = ap.parse_args()
    s = session()
    urls = list_zips(s)
    if args.only:
        urls = [u for u in urls if any(u.endswith(q + "_nport.zip") for q in args.only)]
    print(f"{len(urls)} data sets listed")
    if args.list:
        print("\n".join(urls)); return
    CACHE.mkdir(exist_ok=True)
    mpath = CACHE / "manifest.json"
    manifest = json.loads(mpath.read_text()) if mpath.exists() else {}
    for i, url in enumerate(urls, 1):
        name = url.rsplit("/", 1)[-1]
        dest = CACHE / name
        if name in manifest and dest.exists() and dest.stat().st_size == manifest[name]["bytes"]:
            continue
        time.sleep(PAUSE_S)
        tmp = dest.with_suffix(".part")
        with s.get(url, stream=True, timeout=300) as r:
            r.raise_for_status()
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
        tmp.rename(dest)
        manifest[name] = {"url": url, "bytes": dest.stat().st_size, "sha256": sha256(dest),
                          "downloaded": time.strftime("%Y-%m-%d")}
        mpath.write_text(json.dumps(manifest, indent=1, sort_keys=True))
        print(f"[{i}/{len(urls)}] {name} {dest.stat().st_size/1e6:.1f} MB")
    print(f"done: {len(manifest)} files in {CACHE}")

if __name__ == "__main__":
    main()
