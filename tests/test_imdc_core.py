"""Regression tests for published six-factor IMDC risk grouping."""
import csv
import itertools
import pytest
from imdc_risk import FIELDS, calculate_metrics, process_batch


@pytest.mark.parametrize("count,group", [(0, "Favorable"), (1, "Intermediate"), (2, "Intermediate"), (3, "Poor"), (6, "Poor")])
def test_boundaries(count, group):
    flags = {key: index < count for index, key in enumerate(FIELDS)}
    result = calculate_metrics(**flags)
    assert result["score"] == count
    assert result["classification"] == group
    assert len(result["risk_factors"]) == count


def test_all_64_combinations():
    for values in itertools.product((False, True), repeat=6):
        result = calculate_metrics(**dict(zip(FIELDS, values)))
        assert result["score"] == sum(values)


@pytest.mark.parametrize("bad", ["", "maybe", "2", 2, -1, None, 0.0, float("nan")])
def test_bad_flags(bad):
    inputs = {key: False for key in FIELDS}
    inputs[FIELDS[0]] = bad
    with pytest.raises(ValueError):
        calculate_metrics(**inputs)


def test_missing_or_legacy_fields_rejected():
    with pytest.raises(ValueError):
        calculate_metrics(v1=10.0, v2=2.0)
    with pytest.raises(ValueError):
        calculate_metrics(**{**{key: False for key in FIELDS}, "unrecognized": 1})


def test_batch_absolute_paths_and_spreadsheet_escape(tmp_path):
    inp, out = tmp_path / "in.csv", tmp_path / "out.csv"
    with inp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["case_id", *FIELDS])
        writer.writeheader()
        writer.writerow({"case_id": "=HYPERLINK(1)", **{key: "no" for key in FIELDS}})
        writer.writerow({"case_id": "B", **{key: "yes" for key in FIELDS}})
    assert process_batch(str(inp), str(out)) == 2
    with out.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["score"] == "0"
    assert rows[0]["case_id"].startswith("'=")
    assert rows[1]["score"] == "6"
    assert rows[1]["classification"] == "Poor"


def test_bad_csv_preserves_output(tmp_path):
    inp, out = tmp_path / "bad.csv", tmp_path / "out.csv"
    inp.write_text(",".join(FIELDS) + "\n" + ",".join(["no"] * 5 + ["maybe"]) + "\n")
    out.write_text("unchanged")
    with pytest.raises(ValueError):
        process_batch(str(inp), str(out))
    assert out.read_text() == "unchanged"


def test_inplace_csv_rejected(tmp_path):
    f = tmp_path / "test.csv"
    f.write_text("test")
    with pytest.raises(ValueError):
        process_batch(str(f), str(f))
