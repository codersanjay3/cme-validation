"""test_find_events.py: checks stated_end() and pm_context() on hand-written sentences.
Run from the repo root: python lameduck/test_find_events.py"""
import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from find_events import stated_end, pm_context

T = pd.Timestamp
cases = [
    ("Jane Doe, a portfolio manager of the Fund, will retire effective June 30, 2024.", (T("2024-06-30"), "day")),
    ("John Roe, portfolio manager, is expected to retire on or about March 15, 2025, at which time", (T("2025-03-15"), "day")),
    ("Ms. Doe plans to retire from the Adviser in December 2023 and will remain a portfolio manager until then.", (T("2023-12-31"), "month")),
    ("The portfolio manager intends to retire at the end of the first quarter of 2026.", (T("2026-03-31"), "quarter")),
    ("Mr. Roe, lead manager, has announced his intention to retire by the end of 2022.", (T("2022-12-31"), "year")),
    ("Effective September 1, 2021, Mr. Roe, a portfolio manager of the Fund, will retire.", (T("2021-09-01"), "day_effective_before")),
    ("Mr. Roe, a portfolio manager of the Fund, will retire from the Adviser.", (None, None)),
    ("Mr. Roe, a trustee of the Trust, will retire on June 30, 2024.", (None, None)),
]
ok = True
for txt, want in cases:
    got = stated_end(txt)
    good = got == want
    ok &= good
    print("PASS" if good else "FAIL", got, "|", txt[:70])
pm_ok = pm_context("Jane Doe, a portfolio manager, will retire.") and not pm_context("Jane Doe, a trustee of the Trust, will retire.")
print("PASS" if pm_ok else "FAIL", "pm_context keeps PM and drops trustee")
ok &= pm_ok
print(f"{'all' if ok else 'NOT all'} checks pass")
sys.exit(0 if ok else 1)
