"""
Comparison Demo Tests  --  Multiple Perspectives

"There is a theory which states that if ever anyone discovers exactly
 what the Universe is for and why it is here, it will instantly
 disappear and be replaced by something even more bizarre."

The Comparison demo shows different frameworks tackling the same problem,
like different Guide researchers writing about the same planet.
"""

import pytest
from tests.conftest import assert_success, assert_no_errors


class TestComparison:
    """Integration tests for the Comparison demo."""

    DEMO = "comparison"
    TIMEOUT = 180

    SUCCESS = [
        "Multiple Perspectives",
        "Ford Prefect",
        "Zaphod Beeblebrox",
    ]

    @pytest.mark.integration
    @pytest.mark.fast
    def test_runs_successfully(self, run_demo):
        stdout, stderr, code = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert_no_errors(stdout, stderr, code)
        assert_success(stdout, self.SUCCESS)

    @pytest.mark.integration
    @pytest.mark.fast
    def test_both_frameworks_respond(self, run_demo):
        """Both Strands and LangGraph should produce a response."""
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "Ford Prefect" in stdout and "Strands" in stdout
        assert "Zaphod Beeblebrox" in stdout and "LangGraph" in stdout
        # Check that at least one framework produced a response (not just errors)
        assert "would approve" in stdout or "Response:" in stdout

    @pytest.mark.integration
    @pytest.mark.fast
    def test_perspective_labels(self, run_demo):
        """HHGTTG perspective labels should appear."""
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "Ford Prefect" in stdout or "Zaphod" in stdout, \
            "HHGTTG character perspective labels missing"

    @pytest.mark.integration
    @pytest.mark.fast
    def test_deployment_comparison_shown(self, run_demo):
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "Bedrock Agents" in stdout
        assert "AgentCore" in stdout


class TestComparisonHHGTTG:
    """Theme validation (no AWS needed)."""

    @pytest.mark.hhgttg
    def test_guide_entry_for_earth(self):
        from tests.hhgttg import guide_entry
        assert "harmless" in guide_entry("earth").lower()

    @pytest.mark.hhgttg
    def test_unknown_guide_entry(self):
        from tests.hhgttg import guide_entry
        assert guide_entry("magrathea") == "Mostly harmless."
