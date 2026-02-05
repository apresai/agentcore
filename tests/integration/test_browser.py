"""
Browser Demo Tests  --  The Hitchhiker's Guide

"DON'T PANIC" - inscribed in large, friendly letters on its cover.

Browser sessions let agents explore the web while you watch via
Live View, providing the same reassurance: Don't Panic.
"""

import pytest
from tests.conftest import assert_success, assert_no_errors


class TestBrowser:
    """Integration tests for the Browser demo."""

    DEMO = "browser"
    TIMEOUT = 300

    SUCCESS = [
        "✓ Session started:",
        "✓ Session is",          # READY or ACTIVE
        "Session URLs:",
        "✓ Session stopped",
    ]

    @pytest.mark.integration
    @pytest.mark.medium
    def test_runs_successfully(self, run_demo):
        stdout, stderr, code = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert_no_errors(stdout, stderr, code)
        assert_success(stdout, self.SUCCESS)

    @pytest.mark.integration
    @pytest.mark.medium
    def test_dont_panic_banner(self, run_demo):
        """DON'T PANIC banner should appear."""
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "DON'T PANIC" in stdout, "DON'T PANIC banner missing"

    @pytest.mark.integration
    @pytest.mark.medium
    def test_websocket_urls_shown(self, run_demo):
        """Automation and Live View URLs should appear."""
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "Automation" in stdout
        assert "Live View" in stdout

    @pytest.mark.integration
    @pytest.mark.medium
    def test_session_cleanup(self, run_demo):
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "✓ Session stopped" in stdout


class TestBrowserHHGTTG:
    """Theme validation (no AWS needed)."""

    @pytest.mark.hhgttg
    def test_dont_panic_banner_renders(self):
        from tests.hhgttg import dont_panic_banner
        banner = dont_panic_banner()
        assert "DON'T PANIC" in banner

    @pytest.mark.hhgttg
    def test_guide_entries_exist(self):
        from tests.hhgttg import GUIDE_ENTRIES
        assert "earth" in GUIDE_ENTRIES
        assert "harmless" in GUIDE_ENTRIES["earth"].lower()

    @pytest.mark.hhgttg
    def test_towel_entry(self):
        from tests.hhgttg import GUIDE_ENTRIES
        assert "useful" in GUIDE_ENTRIES["towel"].lower()
