import csv
import pytest
from cli import main as generic_cli
from imdc_risk import FIELDS
from agents.base import AuditTrail


def test_cli_batch_identifies_imdc_schema(tmp_path):
    source, output = tmp_path / "input.csv", tmp_path / "output.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["case_id", *FIELDS])
        writer.writeheader()
        writer.writerow({"case_id": "CASE-01", **{field: "no" for field in FIELDS}})
    assert generic_cli(["batch", "-i", str(source), "-o", str(output)]) == 0
    assert "Favorable" in output.read_text()


def test_cli_rejects_generic_csv_without_required_fields(tmp_path):
    source, output = tmp_path / "input.csv", tmp_path / "output.csv"
    source.write_text("unrelated,value\nX,1\n")
    assert generic_cli(["batch", "-i", str(source), "-o", str(output)]) == 2
    assert not output.exists()


def test_generic_cli_false_string_is_false(tmp_path):
    source, output = tmp_path / "input.csv", tmp_path / "output.csv"
    source.write_text("task_id,target_identifier,primary_metric,is_critical_flag,status_descriptor\nA,KEY-1,5,false,NOMINAL\n")
    assert generic_cli(["batch", "-i", str(source), "-o", str(output)]) == 0
    with output.open(newline="") as handle:
        row = next(csv.DictReader(handle))
    assert row["overall_urgency"] == "ROUTINE"


def test_production_needs_audit_key(monkeypatch):
    monkeypatch.delenv("AUDIT_SECRET_KEY", raising=False)
    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(RuntimeError, match="AUDIT_SECRET_KEY"):
        AuditTrail()
