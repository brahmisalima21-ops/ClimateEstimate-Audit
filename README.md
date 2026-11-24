# ClimateEstimate-Audit

A small toolkit for checking how directly the research literature ties climate risk (physical and transition) to recognized IAS 36 impairment losses and IFRS 9 expected credit losses (ECL), compared with studies that only use credit-risk proxies, disclosure measures or scenario outputs.

This is an early prototype (v0.1.0).

## What's in the repo

- `data/study_registry.csv` - 20 starting records: bibliographic data, sample, outcome variable and directness label
- `data/accounting_frameworks.csv`, `data/risk_taxonomy.csv` - reference tables
- `src/audit_registry.py` - validation, classification and summary counts (standard library only)
- `analysis/gap_analysis.py` - evidence-gap snapshot
- `tests/` - unit tests for the rules that guard against misclassification
- `outputs/` - generated summaries
- `docs/` - classification rules, data dictionary, workflow, source verification log, release checklist

## Running it

Python 3.9+ and nothing else to install.

```bash
python src/audit_registry.py
python analysis/gap_analysis.py
python -m unittest discover -s tests -v
```

## Directness labels

- **D1 Direct**: a recognized IAS 36 impairment or IFRS 9 ECL amount is measured and the framework is confirmed
- **D2 Accounting-linked**: an accounting outcome or test is discussed in substance, but the recognized amount isn't established
- **D3 Proxy**: PD, LGD, EAD, NPL, loan-loss provisions, Z-score or similar indicators
- **D4 Context**: conceptual, disclosure, illustrative or scenario work

None of the 20 records is D1. The labels are rule-based screening tags and still need a person to review them.

## Verification status

Between 13 Oct and 23 Nov 2026 I looked up each record on the publisher, repository or official page. All 20 exist, and titles and authors match. That only confirms bibliographic identity; full-text extraction hasn't been done. The DOI strings for CE-001, 002, 003, 005, 007, 009, 011 and 017 should be opened and compared by hand before anyone cites them. Details are in `docs/source_verification_log.md`.

## Adding or reviewing a record

1. Open the publisher or DOI page, ideally the full text.
2. Fill in `source_verified_date` and update `source_verification_status`.
3. Keep variable names as the source defines them.
4. Mark the recognized amount and framework as Yes only if the source says so explicitly.
5. Put a page, table or section reference in `reviewer_notes`.
6. Run the script and the tests.

## Limits

This is a screening and mapping aid, not a systematic review, and it doesn't cover the literature completely. It says nothing about causality, accounting compliance, search completeness or final inclusion. Empty or unverified fields don't mean something is absent. No full texts are included, so respect publisher copyright if you reuse record contents.

## License

Everything here, code and data, is under the MIT License (`LICENSE`). The bibliographic facts and the source texts belong to their publishers.

## Author

SALIMA BRAHMI

## Citing

See `CITATION.cff`.
