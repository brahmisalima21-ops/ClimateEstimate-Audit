"""Count how much of the registry reaches recognized accounting amounts."""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

with (ROOT / "data" / "study_registry.csv").open(encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

def yes(row, field):
    return row[field].strip().lower() == "yes"

counts = Counter(r["directness_level"] for r in rows)
confirmed = [r for r in rows if yes(r, "recognized_accounting_amount_measured")
             and yes(r, "accounting_framework_confirmed")]
flags = ("pending", "revalidation", "not verified", "unconfirmed")
incomplete = [r for r in rows
              if any(k in r["source_verification_status"].lower() for k in flags)
              or not r["source_verified_date"].strip()]

report = ROOT / "outputs" / "evidence_gap_snapshot.md"
with report.open("w", encoding="utf-8") as f:
    f.write("# Evidence-gap snapshot\n\n")
    f.write(f"- Records loaded: **{len(rows)}**\n")
    f.write(f"- Records with unfinished source verification: **{len(incomplete)}** "
            "(a date only means a spot-check was done)\n")
    f.write(f"- Records with a confirmed recognized amount and framework: **{len(confirmed)}**\n\n")
    f.write("## Directness counts\n\n")
    for k in sorted(counts):
        f.write(f"- {k}: {counts[k]}\n")
    f.write("\nSee docs/source_verification_log.md for the verification status.\n")
print(f"Wrote {report.relative_to(ROOT)}")
