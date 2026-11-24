#!/usr/bin/env python3
"""Validate the study registry and write simple summary counts (stdlib only)."""
import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "study_registry.csv"
OUTPUTS = ROOT / "outputs"

REQUIRED = {
    "study_id", "title", "doi_or_url", "source_verification_status",
    "recognized_accounting_amount_measured", "accounting_framework_confirmed",
    "directness_level",
}
VALID_DIRECTNESS = {"D1", "D2", "D3", "D4"}
YES = {"yes", "true", "1"}

PROXY_TERMS = (
    "pd", "lgd", "ead", "npl", "llp", "loan quality", "z-score",
    "capital resilience", "bank performance", "impairment proxy", "auditor fees",
)
ACCOUNTING_TERMS = (
    "impairment test", "recognized impairment", "recognised impairment",
    "expected credit loss", "ecl amount", "carrying amount",
)


def load_rows(path=REGISTRY):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Registry is missing columns: {sorted(missing)}")
        return list(reader)


def is_yes(row, field):
    return str(row.get(field, "")).strip().lower() in YES


def has_term(text, terms):
    """Whole-word match, so 'pd' doesn't hit 'updated' and 'ead' doesn't hit 'spread'."""
    return any(
        re.search(r"(?<![a-z0-9])" + re.escape(t) + r"(?![a-z0-9])", text)
        for t in terms
    )


def classify_directness(row):
    """Rule-based screening tag. Naming a standard is never enough for D2."""
    recognized = is_yes(row, "recognized_accounting_amount_measured")
    confirmed = is_yes(row, "accounting_framework_confirmed")
    if recognized and confirmed:
        return "D1"
    if recognized or confirmed:
        return "D2"

    variable = str(row.get("variable_type", "")).strip().lower()
    outcome = str(row.get("accounting_outcome", "")).strip().lower()
    if has_term(variable, PROXY_TERMS) or has_term(outcome, PROXY_TERMS):
        return "D3"
    if has_term(outcome, ACCOUNTING_TERMS):
        return "D2"
    return "D4"


def validate(rows):
    errors, warnings = [], []
    seen = set()
    for row in rows:
        sid = row.get("study_id", "").strip()
        level = row.get("directness_level", "")

        if not sid:
            errors.append("Missing study_id")
        elif sid in seen:
            errors.append(f"Duplicate study_id: {sid}")
        seen.add(sid)

        if not row.get("title", "").strip():
            errors.append(f"{sid}: missing title")
        if not row.get("doi_or_url", "").strip():
            warnings.append(f"{sid}: missing DOI/URL")

        if level not in VALID_DIRECTNESS:
            errors.append(f"{sid}: invalid directness level")
        else:
            expected = classify_directness(row)
            if level != expected:
                errors.append(f"{sid}: stored {level} but classifier gives {expected}")

        recognized = is_yes(row, "recognized_accounting_amount_measured")
        confirmed = is_yes(row, "accounting_framework_confirmed")
        if recognized and not confirmed:
            warnings.append(f"{sid}: recognized amount is Yes but framework is not confirmed")
        if level == "D1" and not (recognized and confirmed):
            errors.append(f"{sid}: D1 needs both recognized amount and framework confirmed")

        if not row.get("source_verified_date", "").strip():
            warnings.append(f"{sid}: no source verification date")
        status = row.get("source_verification_status", "").lower()
        if "pending" in status or "revalidation" in status:
            warnings.append(f"{sid}: source verification not finished")
    return errors, warnings


def write_summary(rows):
    OUTPUTS.mkdir(exist_ok=True)
    directness = Counter(r.get("directness_level", "Unknown") for r in rows)
    risks = Counter(r.get("climate_risk_type", "Unknown") for r in rows)

    with (OUTPUTS / "directness_counts.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["directness_level", "record_count"])
        for level in sorted(directness):
            w.writerow([level, directness[level]])

    with (OUTPUTS / "risk_type_counts.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["climate_risk_type", "record_count"])
        for risk, n in sorted(risks.items()):
            w.writerow([risk, n])

    with (OUTPUTS / "registry_audit.md").open("w", encoding="utf-8") as f:
        f.write("# Registry audit summary\n\n")
        f.write(f"Records in registry: **{len(rows)}**\n\n")
        f.write("## Directness counts\n\n")
        for level in sorted(directness):
            f.write(f"- {level}: {directness[level]}\n")
        f.write("\n## Risk labels (some are compound)\n\n")
        for risk, n in sorted(risks.items()):
            f.write(f"- {risk}: {n}\n")
        f.write("\nSee docs/source_verification_log.md for the verification status.\n")


def main():
    rows = load_rows()
    errors, warnings = validate(rows)
    print(f"Loaded {len(rows)} records.")
    if errors:
        print("ERRORS:")
        for e in errors:
            print(" -", e)
    if warnings:
        print(f"Warnings: {len(warnings)}")
        for w in warnings[:10]:
            print(" -", w)
        if len(warnings) > 10:
            print(f" ... and {len(warnings) - 10} more")
    if not errors:
        write_summary(rows)
        print("Validation passed. Summaries written to outputs/.")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
