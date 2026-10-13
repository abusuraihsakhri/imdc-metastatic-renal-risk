"""Compatibility regression tests for the IMDC CLI functions."""
import csv
from imdc_risk import FIELDS, calculate_metrics, process_batch


def test_imdc_risk_single():
    flags = {key: "no" for key in FIELDS}
    flags[FIELDS[0]] = "yes"
    result = calculate_metrics(**flags)
    assert result["score"] == 1
    assert result["classification"] == "Intermediate"


def test_imdc_risk_batch(tmp_path):
    source, output = tmp_path / "in.csv", tmp_path / "out.csv"
    with source.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", *FIELDS])
        writer.writeheader()
        writer.writerow({"case_id": "CASE-A", **{key: "no" for key in FIELDS}})
    assert process_batch(str(source), str(output)) == 1
    assert "Favorable" in output.read_text(encoding="utf-8")
