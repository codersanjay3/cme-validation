"""
test_build_panel.py: checks build_panel.py on a hand-built data set whose
answers are worked out below. Run: python rebuild_13f/test_build_panel.py

Filer 1 crosses the 2023 unit change: 2022Q3 filed in thousands, 2022Q4 in dollars.
  Q3: AAA 100 sh, value 1 ($1,000, $10/sh); BBB 50 sh, value 1 ($1,000, $20/sh).
  Q4: AAA 100 sh, value 1,000 ($10/sh); CCC 25 sh, value 1,000 ($40/sh). BBB exited.
  Common prices: AAA $10 (both filers), BBB no Q4 holder -> Q3 price $20, CCC $40.
  trades = 50*20 + 25*40 = 2,000; v0 = 1,000 + 1,000 = 2,000; v1 = 1,000 + 1,000 = 2,000
  turnover = 0.5*2,000 / (0.5*4,000) = 0.5 -> tau = 126.
  Without the unit fix Q3 would be read as $1 and $1, giving a wildly different number.
Filer 2 tests amendments and row filters.
  Q3 original (filed 2022-11-01): AAA 100 sh, value 1. Q3 RESTATEMENT (filed 2023-01-20, dollars):
  AAA 200 sh, value 2,000. Base for Q3 = restatement -> AAA 200 at $10.
  Q4 original (filed 2023-02-01): AAA 200 sh, value 2,000, plus a PUT row and a PRN row (both dropped).
  Q4 NEW HOLDINGS amendment (filed 2023-03-01): DDD 10 sh, value 500 ($50).
  trades = 10*50 = 500; v0 = 2,000; v1 = 2,000 + 500 = 2,500 -> turnover = 0.5*500/(0.5*4,500) = 0.1111
Filer 3 tests the split rebase: EEE 100 sh at $100 (value 10, thousands) -> 200 sh at $50 (value 10,000).
  raw: trades = 100*50 = 5,000; v0 = 5,000; v1 = 10,000 -> 0.3333. split-rebased: no trade -> turnover 0.
A 13F-NT notice (filer 4) must be ignored.
"""
import io, sys, tempfile, zipfile
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_panel as bp

SUB = ["ACCESSION_NUMBER", "FILING_DATE", "SUBMISSIONTYPE", "CIK", "PERIODOFREPORT"]
COV = ["ACCESSION_NUMBER", "REPORTCALENDARORQUARTER", "ISAMENDMENT", "AMENDMENTNO", "AMENDMENTTYPE", "REPORTTYPE"]
INF = ["ACCESSION_NUMBER", "INFOTABLE_SK", "NAMEOFISSUER", "TITLEOFCLASS", "CUSIP", "VALUE", "SSHPRNAMT",
       "SSHPRNAMTTYPE", "PUTCALL", "INVESTMENTDISCRETION"]

subs = [("A1", "10-NOV-2022", "13F-HR", "0000000001", "30-SEP-2022"),
        ("A2", "10-FEB-2023", "13F-HR", "0000000001", "31-DEC-2022"),
        ("B1", "01-NOV-2022", "13F-HR", "0000000002", "30-SEP-2022"),
        ("B2", "20-JAN-2023", "13F-HR/A", "0000000002", "30-SEP-2022"),
        ("B3", "01-FEB-2023", "13F-HR", "0000000002", "31-DEC-2022"),
        ("B4", "01-MAR-2023", "13F-HR/A", "0000000002", "31-DEC-2022"),
        ("C1", "05-NOV-2022", "13F-HR", "0000000003", "30-SEP-2022"),
        ("C2", "05-FEB-2023", "13F-HR", "0000000003", "31-DEC-2022"),
        ("D1", "05-FEB-2023", "13F-NT", "0000000004", "31-DEC-2022")]
covs = [("A1", "30-SEP-2022", "N", "", "", "13F HOLDINGS REPORT"),
        ("A2", "31-DEC-2022", "N", "", "", "13F HOLDINGS REPORT"),
        ("B1", "30-SEP-2022", "N", "", "", "13F HOLDINGS REPORT"),
        ("B2", "30-SEP-2022", "Y", "1", "RESTATEMENT", "13F HOLDINGS REPORT"),
        ("B3", "31-DEC-2022", "N", "", "", "13F HOLDINGS REPORT"),
        ("B4", "31-DEC-2022", "Y", "1", "NEW HOLDINGS", "13F HOLDINGS REPORT"),
        ("C1", "30-SEP-2022", "N", "", "", "13F HOLDINGS REPORT"),
        ("C2", "31-DEC-2022", "N", "", "", "13F HOLDINGS REPORT"),
        ("D1", "31-DEC-2022", "N", "", "", "13F NOTICE")]
infs = [("A1", "AAA000001", "1", "100", "SH", ""), ("A1", "BBB000001", "1", "50", "SH", ""),
        ("A2", "AAA000001", "1000", "100", "SH", ""), ("A2", "CCC000001", "1000", "25", "SH", ""),
        ("B1", "AAA000001", "1", "100", "SH", ""),
        ("B2", "AAA000001", "2000", "200", "SH", ""),
        ("B3", "AAA000001", "2000", "200", "SH", ""), ("B3", "AAA000001", "300", "10", "SH", "Put"),
        ("B3", "ZZZ000001", "900", "1000", "PRN", ""),
        ("B4", "DDD000001", "500", "10", "SH", ""),
        ("C1", "EEE000001", "10", "100", "SH", ""), ("C2", "EEE000001", "10000", "200", "SH", ""),
        ("D1", "AAA000001", "5", "5", "SH", "")]

def tsv(cols, rows):
    return "\t".join(cols) + "\n" + "\n".join("\t".join(r) for r in rows) + "\n"

def write_fixture(folder):
    z = Path(folder) / "01oct2022-31mar2023_form13f.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("SUBMISSION.tsv", tsv(SUB, subs))
        zf.writestr("COVERPAGE.tsv", tsv(COV, covs))
        zf.writestr("INFOTABLE.tsv", tsv(INF, [(a, str(i), "X", "COM", c, v, s, t, p, "SOLE")
                                              for i, (a, c, v, s, t, p) in enumerate(infs)]))
    return z

if len(sys.argv) > 1 and sys.argv[1] == "--write-fixture":
    print(write_fixture(sys.argv[2])); sys.exit(0)

with tempfile.TemporaryDirectory() as d:
    z = write_fixture(d)
    filings, info = bp.load_zip(z, {})
    use = bp.resolve_amendments(filings)
    info = info.merge(filings[["accession", "filing_date"]], on="accession").merge(use, on="accession")
    info["value_usd"] = info.value_raw.where(info.filing_date >= bp.UNIT_CUTOFF, info.value_raw * 1000)
    pos = info.groupby(["cik", "period", "cusip"], as_index=False)[["shares", "value_usd"]].sum()
    tau = bp.turnover_panel(pos).set_index("cik")

checks = {
    "notice filing ignored": "4" not in set(filings.cik),
    "put and PRN rows dropped": not ((pos.cik == "2") & pos.cusip.isin(["ZZZ000001"])).any() and
        pos[(pos.cik == "2") & (pos.period == "2022Q4") & (pos.cusip == "AAA000001")].shares.item() == 200,
    "restatement replaces original": pos[(pos.cik == "2") & (pos.period == "2022Q3")].shares.sum() == 200,
    "new-holdings amendment added": ((pos.cik == "2") & (pos.period == "2022Q4") & (pos.cusip == "DDD000001")).any(),
    "unit fix: Q3 value in dollars": abs(pos[(pos.cik == "1") & (pos.period == "2022Q3")].value_usd.sum() - 2000) < 1e-9,
    "filer 1 turnover 0.5": abs(tau.loc["1", "turnover"] - 0.5) < 1e-9,
    "filer 1 tau 126": abs(tau.loc["1", "tau"] - 126) < 1e-9,
    "filer 2 turnover 1/9": abs(tau.loc["2", "turnover"] - 1 / 9) < 1e-9,
    "filer 3 raw turnover 1/3": abs(tau.loc["3", "turnover"] - 1 / 3) < 1e-9,
    "filer 3 split-rebased turnover 0": abs(tau.loc["3", "turnover_split"]) < 1e-9,
}
for k, v in checks.items():
    print(("PASS " if v else "FAIL ") + k)
sys.exit(0 if all(checks.values()) else 1)
