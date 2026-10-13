#!/usr/bin/env python3
"""IMDC (Heng) six-factor prognostic risk stratification for metastatic RCC.

Each input is an assessed adverse-factor flag, not a laboratory measurement.
Determine abnormal laboratory flags using the relevant local reference limits.
This is prognostic grouping, not a treatment or emergency recommendation.
"""

import argparse
import csv
import json
import os
from pathlib import Path

CRITERIA = (
    ("kps_below_80", "Karnofsky performance status <80%"),
    ("diagnosis_to_treatment_lt_1yr", "Diagnosis to systemic treatment <1 year"),
    ("hemoglobin_below_lln", "Hemoglobin below laboratory LLN"),
    ("corrected_calcium_above_uln", "Corrected calcium above laboratory ULN"),
    ("neutrophils_above_uln", "Neutrophil count above laboratory ULN"),
    ("platelets_above_uln", "Platelet count above laboratory ULN"),
)
FIELDS = tuple(name for name, _ in CRITERIA)


def _parse_bool(value, field):
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned in ("yes", "true", "1"):
            return True
        if cleaned in ("no", "false", "0"):
            return False
    raise ValueError(f"{field} must be yes/no, true/false or 1/0; got {value!r}")


def calculate_metrics(**kwargs):
    """Count all six equally weighted adverse factors (0 / 1–2 / 3–6)."""
    missing = [name for name in FIELDS if name not in kwargs]
    unknown = [name for name in kwargs if name not in FIELDS]
    if missing or unknown:
        raise ValueError(f"Exactly six IMDC factors required; missing={missing}, unknown={unknown}")
    flags = {name: _parse_bool(kwargs[name], name) for name in FIELDS}
    score = sum(flags.values())
    risk_group = "Favorable" if score == 0 else "Intermediate" if score < 3 else "Poor"
    return {
        "tool": "imdc-metastatic-renal-risk",
        "score": score,
        "classification": risk_group,
        "risk_factors": [label for key, label in CRITERIA if flags[key]],
        "factors": flags,
        "inputs_evaluated": 6,
        "clinical_recommendation": "Prognostic grouping only; clinical management requires independent assessment.",
    }


def _validate_csv_path(filepath, *, allow_absolute=False):
    """Reject parent traversal; accept absolute paths only from trusted local CLI."""
    raw = os.fspath(filepath)
    if not raw or "\x00" in raw:
        raise ValueError("Invalid file path")
    if raw.startswith(("\\", "//")) or (len(raw) >= 2 and raw[1] == ":"):
        raise ValueError("Path traversal not allowed")
    path = Path(raw)
    if ".." in path.parts or (path.is_absolute() and not allow_absolute):
        raise ValueError("Path traversal not allowed")
    return os.path.normpath(raw)


def _spreadsheet_safe(value):
    """Prevent metadata cells from being evaluated as spreadsheet formulas."""
    s = "" if value is None else str(value)
    if s.lstrip().startswith(("=", "+", "-", "@")) or s.startswith(("\t", "\r", "\n")):
        return "'" + s
    return s


def process_batch(input_csv, output_csv):
    """Validate all local CSV records before creating/writing the output file."""
    src = _validate_csv_path(input_csv, allow_absolute=True)
    dst = _validate_csv_path(output_csv, allow_absolute=True)
    if Path(src).resolve() == Path(dst).resolve():
        raise ValueError("Input and output must be different paths")
    with open(src, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)) or any(key not in headers for key in FIELDS):
            raise ValueError("CSV must contain six unique IMDC factor columns")
        if not all(headers) or len(headers) > 100:
            raise ValueError("Invalid CSV headers")
        rows = []
        for index, row in enumerate(reader, start=2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"CSV row {index}: incorrect number of columns")
            try:
                result = calculate_metrics(**{key: row[key] for key in FIELDS})
            except ValueError as error:
                raise ValueError(f"CSV row {index}: {error}") from error
            clean = {key: _spreadsheet_safe(value) for key, value in row.items()}
            clean["score"] = result["score"]
            clean["classification"] = result["classification"]
            rows.append(clean)
    with open(dst, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers + ["score", "classification"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description="IMDC (Heng) metastatic RCC six-factor prognostic score")
    commands = parser.add_subparsers(dest="command", required=True)
    single = commands.add_parser("single", help="Score one de-identified case")
    for name in FIELDS:
        single.add_argument("--" + name.replace("_", "-"), required=True, choices=("yes", "no"))
    batch = commands.add_parser("batch", help="Score a CSV file locally")
    batch.add_argument("-i", "--input", required=True)
    batch.add_argument("-o", "--output", default="results.csv")
    args = parser.parse_args(argv)
    if args.command == "single":
        print(json.dumps(calculate_metrics(**{name: getattr(args, name) for name in FIELDS}), indent=2))
    else:
        print(f"Processed {process_batch(args.input, args.output)} rows -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
