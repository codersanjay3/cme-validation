"""
Fixture test for build_fund_panel.py: two synthetic N-PORT zips with known answers.
Run from the repo root: python nport_panel/test_build_fund_panel.py
"""
import io, json, subprocess, sys, tempfile, zipfile
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INFO_EXTRA = ["SALES_FLOW_MON1", "SALES_FLOW_MON2", "SALES_FLOW_MON3", "REDEMPTION_FLOW_MON1", "REDEMPTION_FLOW_MON2",
              "REDEMPTION_FLOW_MON3", "REINVESTMENT_FLOW_MON1", "REINVESTMENT_FLOW_MON2", "REINVESTMENT_FLOW_MON3"]


def tsv(rows, cols):
    return pd.DataFrame(rows, columns=cols).to_csv(sep="\t", index=False)


def write_zip(path, subs, holds, rets):
    """subs: (acc, filing_date, sub_type, report_date, series, net_assets); holds: (acc, cusip, bal, unit, value, payoff, cat)."""
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("SUBMISSION.tsv", tsv([(a, f, t, r) for a, f, t, r, s, n in subs],
                                         ["ACCESSION_NUMBER", "FILING_DATE", "SUB_TYPE", "REPORT_DATE"]))
        z.writestr("REGISTRANT.tsv", tsv([(a, "0000000001") for a, *_ in subs], ["ACCESSION_NUMBER", "CIK"]))
        z.writestr("FUND_REPORTED_INFO.tsv", tsv([(a, s, "Fund " + s, n) + (0,) * 9 for a, f, t, r, s, n in subs],
                                                 ["ACCESSION_NUMBER", "SERIES_ID", "SERIES_NAME", "NET_ASSETS"] + INFO_EXTRA))
        z.writestr("MONTHLY_TOTAL_RETURN.tsv", tsv(rets, ["ACCESSION_NUMBER", "MONTHLY_TOTAL_RETURN1",
                                                          "MONTHLY_TOTAL_RETURN2", "MONTHLY_TOTAL_RETURN3"]))
        z.writestr("FUND_REPORTED_HOLDING.tsv", tsv(holds, ["ACCESSION_NUMBER", "ISSUER_CUSIP", "BALANCE", "UNIT",
                                                            "CURRENCY_VALUE", "PAYOFF_PROFILE", "ASSET_CAT"]))


def main():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d); cache = d / "cache"; cache.mkdir()
        # Fund S1: Dec-2022 report holds A 100 @10, B 100 @10. Mar-2023 holds A 100, B 50, C 50 @10.
        #   traded |dB|=50 -> 500, |dC|=50 -> 500; turnover = 0.5*1000 / (0.5*(2000+2000)) = 0.25
        #   selling exactly half of B is a trade, not a reverse split (price unchanged): split variant also 0.25
        # The original Mar-2023 filing (acc a3) is replaced by an amendment (a4) with the true holdings.
        # Fund S2: stock F splits 2:1 between reports (100 -> 200), no other trade: split variant 0.
        # Fund S3: pure inflow, G 100 -> 200 at unchanged price 10: share ratio 2 but price ratio 1, so a
        #   trade: turnover = 0.5*1000 / (0.5*(1000+2000)) = 1/3; min(buys, sells) turnover = 0.
        # Junk rows (bond, short, principal units, bad CUSIP) must be dropped.
        write_zip(cache / "2023q1_nport.zip",
                  [("a1", "20-JAN-2023", "NPORT-P", "31-DEC-2022", "S1", 2000),
                   ("b1", "20-JAN-2023", "NPORT-P", "31-DEC-2022", "S2", 1000),
                   ("c1", "20-JAN-2023", "NPORT-P", "31-DEC-2022", "S3", 1000)],
                  [("a1", "AAAAAAAA1", 100, "NS", 1000, "Long", "EC"), ("a1", "BBBBBBBB2", 100, "NS", 1000, "Long", "EC"),
                   ("a1", "DDDDDDDD4", 100, "PA", 1000, "Long", "DBT"), ("a1", "EEEEEEEE5", 10, "NS", 100, "Short", "EC"),
                   ("a1", "000000000", 10, "NS", 100, "Long", "EC"), ("a1", "N/A", 10, "NS", 100, "Long", "EC"),
                   ("b1", "FFFFFFFF6", 100, "NS", 1000, "Long", "EC"), ("c1", "GGGGGGGG7", 100, "NS", 1000, "Long", "EC")],
                  [("a1", 1.0, 2.0, 3.0), ("b1", 0.5, 0.5, 0.5), ("c1", 0.0, 0.0, 0.0)])
        write_zip(cache / "2023q2_nport.zip",
                  [("a3", "20-APR-2023", "NPORT-P", "31-MAR-2023", "S1", 2000),
                   ("a4", "25-APR-2023", "NPORT-P/A", "31-MAR-2023", "S1", 2000),
                   ("b3", "20-APR-2023", "NPORT-P", "31-MAR-2023", "S2", 1000),
                   ("c3", "20-APR-2023", "NPORT-P", "31-MAR-2023", "S3", 2000)],
                  [("a3", "AAAAAAAA1", 1, "NS", 10, "Long", "EC"),
                   ("a4", "AAAAAAAA1", 100, "NS", 1000, "Long", "EC"), ("a4", "BBBBBBBB2", 50, "NS", 500, "Long", "EC"),
                   ("a4", "CCCCCCCC3", 50, "NS", 500, "Long", "EC"),
                   ("b3", "FFFFFFFF6", 200, "NS", 1000, "Long", "EC"), ("c3", "GGGGGGGG7", 200, "NS", 2000, "Long", "EC")],
                  [("a4", 1.0, 1.0, 1.0), ("b3", 0.0, 0.0, 0.0), ("c3", 0.0, 0.0, 0.0)])
        out = d / "out"
        r = subprocess.run([sys.executable, str(ROOT / "nport_panel" / "build_fund_panel.py"), "--cache", str(cache),
                            "--out", str(out)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        rep = pd.read_parquet(out / "reports.parquet")
        tau = pd.read_parquet(out / "tau.parquet").set_index("series_id")
        checks = {
            "amendment replaces original": set(rep.accession) == {"a1", "b1", "c1", "a4", "b3", "c3"},
            "junk holdings dropped (S1 Dec has 2 stocks)": int(rep.set_index("accession").loc["a1", "n_stocks"]) == 2,
            "S1 turnover 0.25": abs(tau.loc["S1", "turnover"] - 0.25) < 1e-9,
            "S1 half-sale not a split": abs(tau.loc["S1", "turnover_split"] - 0.25) < 1e-9,
            "S1 tau 252": abs(tau.loc["S1", "tau"] - 252) < 1e-6,
            "S1 gap 3 months, period 2023Q1": tau.loc["S1", "gap_months"] == 3 and tau.loc["S1", "period"] == "2023Q1",
            "S2 split variant zero turnover": tau.loc["S2", "turnover_split"] < 1e-9,
            "S2 raw turnover counts split as trade": tau.loc["S2", "turnover"] > 0.1,
            "S1 min(buys, sells) turnover 0.25": abs(tau.loc["S1", "turnover_min"] - 0.25) < 1e-9,
            "S3 inflow is a trade, turnover 1/3": abs(tau.loc["S3", "turnover_split"] - 1 / 3) < 1e-9,
            "S3 inflow nets out of min turnover": tau.loc["S3", "turnover_min"] < 1e-9,
            "returns median across classes kept": abs(rep.set_index("accession").loc["a1", "monthly_total_return2"] - 2.0) < 1e-9,
        }
        for k, v in checks.items():
            print(("PASS " if v else "FAIL ") + k)
        if not all(checks.values()):
            print(tau.T)
            for f in sorted((out / "holdings").glob("*.parquet")):
                print(f.name); print(pd.read_parquet(f))
            sys.exit(1)
        print(f"{sum(checks.values())}/{len(checks)} checks pass")


if __name__ == "__main__":
    main()
