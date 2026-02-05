"""
Gateway Demo Tests  --  The Babel Fish

"The Babel fish is small, yellow, leech-like, and probably the
 oddest thing in the Universe."

Gateway translates any API protocol into MCP, just as the Babel fish
translates any language into something you can understand.
"""

import pytest
from tests.conftest import assert_success, assert_no_errors


class TestGateway:
    """Integration tests for the Gateway demo."""

    DEMO = "gateway"
    TIMEOUT = 300  # Gateway + IAM role creation

    SUCCESS = [
        "✓ IAM role ready:",
        "✓ Gateway created:",
        "✓ Gateway is",       # READY or ACTIVE
        "✓ Gateway working successfully!",
    ]

    @pytest.mark.integration
    @pytest.mark.medium
    def test_runs_successfully(self, run_demo):
        stdout, stderr, code = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert_no_errors(stdout, stderr, code)
        assert_success(stdout, self.SUCCESS)

    @pytest.mark.integration
    @pytest.mark.medium
    def test_mcp_protocol_shown(self, run_demo):
        """Gateway should advertise MCP protocol."""
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "MCP" in stdout, "MCP protocol not mentioned"

    @pytest.mark.integration
    @pytest.mark.medium
    def test_babel_fish_banner(self, run_demo):
        """Babel Fish theme should be present."""
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "Babel Fish" in stdout, "Babel Fish banner missing"

    @pytest.mark.integration
    @pytest.mark.medium
    def test_cleanup_completed(self, run_demo):
        """All resources must be cleaned up."""
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "✓ Gateway deleted" in stdout
        assert "✓ IAM role deleted" in stdout

    @pytest.mark.integration
    @pytest.mark.medium
    def test_gateway_endpoint_shown(self, run_demo):
        """The MCP endpoint URL should be printed."""
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "gateway.bedrock-agentcore" in stdout, "Gateway endpoint URL missing"


class TestGatewayHHGTTG:
    """Theme validation (no AWS needed)."""

    @pytest.mark.hhgttg
    def test_babel_fish_entry(self):
        from tests.hhgttg import GUIDE_ENTRIES
        entry = GUIDE_ENTRIES["babel_fish"]
        assert "yellow" in entry.lower()
        assert "leech" in entry.lower()

    @pytest.mark.hhgttg
    def test_babel_fish_banner_renders(self):
        from tests.hhgttg import babel_fish_banner
        banner = babel_fish_banner()
        assert "Babel Fish" in banner
        assert "MCP" in banner
