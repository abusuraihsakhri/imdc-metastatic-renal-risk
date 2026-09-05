"""
Pytest configuration for imdc-metastatic-renal-risk.
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Set development audit key for tests
os.environ.setdefault("AUDIT_SECRET_KEY", "test-audit-key-for-testing-only")
