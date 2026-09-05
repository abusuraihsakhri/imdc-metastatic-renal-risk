"""
Security-focused tests for imdc-metastatic-renal-risk.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import os

from agents.base import PHIGuard, AuditTrail, SecurityException
from imdc_risk import _validate_csv_path, process_batch


class TestPathTraversalProtection:
    """Test that file path validation prevents directory traversal."""

    def test_reject_parent_directory_traversal(self):
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            _validate_csv_path("../etc/passwd")

    def test_reject_absolute_path(self):
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            _validate_csv_path("/etc/passwd")

    def test_accept_safe_relative_path(self):
        result = _validate_csv_path("data/input.csv")
        assert result == os.path.normpath("data/input.csv")

    def test_accept_simple_filename(self):
        result = _validate_csv_path("input.csv")
        assert result == "input.csv"

    def test_process_batch_rejects_traversal(self):
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            process_batch("../etc/passwd", "output.csv")

    def test_process_batch_rejects_traversal_output(self):
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            process_batch("input.csv", "../etc/output.csv")


class TestPHIGuard:
    """Test PHI detection and redaction."""

    def test_detect_mrn(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-12345678")

    def test_detect_ssn(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_detect_phone(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Call 555-123-4567")

    def test_detect_email(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Email: patient@example.com")

    def test_clean_text_passes(self):
        PHIGuard.assert_no_phi("Specimen KEY-001 optimal parameters")

    def test_redact_phi(self):
        result = PHIGuard.redact_phi("Patient MRN-12345678 is stable")
        assert "REDACTED_IDENTIFIER" in result
        assert "MRN-12345678" not in result


class TestAuditTrailSecurity:
    """Test audit trail security features."""

    def test_audit_trail_with_explicit_key(self):
        trail = AuditTrail(secret_key="test-key-12345")
        entry = trail.log("test", "test_tier", "TEST_EVENT", {"data": "value"})
        assert entry["current_hash"] != ""
        assert entry["prev_hash"] == "GENESIS_BLOCK_0000000000000000"

    def test_audit_trail_warns_without_key(self):
        """Without AUDIT_SECRET_KEY, a warning is issued for development."""
        original = os.environ.pop("AUDIT_SECRET_KEY", None)
        try:
            import warnings
            with pytest.warns(RuntimeWarning, match="AUDIT_SECRET_KEY not set"):
                trail = AuditTrail()
            # Should still work with development fallback
            assert trail.secret_key == b"DEV-KEY-CHANGE-ME-IN-PRODUCTION"
        finally:
            if original:
                os.environ["AUDIT_SECRET_KEY"] = original

    def test_audit_trail_integrity(self):
        trail = AuditTrail(secret_key="integrity-test-key")
        trail.log("actor1", "tier1", "EVENT1", {"a": 1})
        trail.log("actor2", "tier2", "EVENT2", {"b": 2})
        trail.log("actor3", "tier3", "EVENT3", {"c": 3})
        assert trail.verify_integrity() is True

    def test_audit_trail_tamper_detection(self):
        trail = AuditTrail(secret_key="tamper-test-key")
        trail.log("actor1", "tier1", "EVENT1", {"a": 1})
        trail.log("actor2", "tier2", "EVENT2", {"b": 2})
        # Tamper with the first entry
        trail.logs[0]["payload_hash"] = "tampered_hash"
        assert trail.verify_integrity() is False
