"""
download.py: fetch the SEC "Form 13F Data Sets" (all filers, 2013Q2 onward).

Step 0 of the pivot (docs/novelty-audit/IDEAS.md, idea 1): replace the top-150
EDGAR scrape with the full filer universe and share counts.

The SEC requires a User-Agent with a real contact. Set your own once:
    export SEC_CONTACT_EMAIL="you@example.com"     (e.g. in ~/.zshrc)
The script refuses to run without it.

Usage (from the repo root):
    python rebuild_13f/download.py            # list + download every data set
    python rebuild_13f/download.py --list     # only list what is available
Files land in sec13f_cache/ (gitignored) with sec13f_cache/manifest.json
recording URL, size and sha256 for each zip. Re-running skips complete files.
Polite: one request at a time, a pause between requests (SEC fair-access
policy allows at most 10 requests per second; we stay far below).
"""
import argparse, hashlib, json, os, re, sys, time
from pathlib import Path
from urllib.parse import urljoin
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "sec13f_cache"
INDEX_URL = "https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets"
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
    links = sorted(set(re.findall(r'href="([^"]+form13f[^"]*\.zip)"', r.text, flags=re.I)))
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
    args = ap.parse_args()
    s = session()
    urls = list_zips(s)
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
