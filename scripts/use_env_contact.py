"""One-time fix: replace a hardcoded SEC User-Agent contact with the SEC_CONTACT_EMAIL env var.

Run from the repo root:  python3 scripts/use_env_contact.py
SEC EDGAR requires a real contact in the User-Agent; each person sets their own:
    export SEC_CONTACT_EMAIL="you@example.com"
"""
import re

FILES = ["bond_by_type.py", "bond_discover.py", "bond_empirical.py",
         "causal_identification.py", "empirical_tdi.py"]
PAT = re.compile(r"""(["'])((?:CME-Validation|research) )[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\1""")


def repl(m):
    q = m.group(1)
    return (f"{q}{m.group(2)}{q} + os.environ.get({q}SEC_CONTACT_EMAIL{q}, "
            f"{q}set-SEC_CONTACT_EMAIL{q})")


for f in FILES:
    s = open(f).read()
    s, n = PAT.subn(repl, s)
    if n and not re.search(r"^import os\b|^import .*\bos\b", s, re.M):
        m = re.search(r"^(import|from) .*$", s, re.M)
        s = s[:m.start()] + "import os\n" + s[m.start():]
    open(f, "w").write(s)
    print(f, "replaced", n)
