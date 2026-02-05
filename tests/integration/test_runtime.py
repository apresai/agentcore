"""
Runtime Demo Tests  --  Deep Thought

"The Answer to the Great Question ... of Life, the Universe and
 Everything ... Is ... Forty-two."

The Runtime demo asks an LLM the Ultimate Question and expects 42.
"""

import pytest
from tests.conftest import assert_success, assert_no_errors


class TestRuntime:
    """Integration tests for the Runtime demo."""

    DEMO = "runtime"
    TIMEOUT = 120

    SUCCESS = [
        "✓ Agent created successfully",
        "✓ Local test passed",
        "✓ Ready for deployment!",
    ]

    @pytest.mark.integration
    @pytest.mark.fast
    def test_runs_successfully(self, run_demo):
        stdout, stderr, code = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert_no_errors(stdout, stderr, code)
        assert_success(stdout, self.SUCCESS)

    @pytest.mark.integration
    @pytest.mark.fast
    def test_answer_is_42(self, run_demo):
        """Deep Thought's answer must appear in the output."""
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "42" in stdout, "The Answer to Life, the Universe and Everything is missing"

    @pytest.mark.integration
    @pytest.mark.fast
    def test_deep_thought_banner(self, run_demo):
        """The demo should show the Deep Thought banner."""
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "DEEP THOUGHT" in stdout, "Deep Thought banner missing"

    @pytest.mark.integration
    @pytest.mark.fast
    def test_deployment_commands_shown(self, run_demo):
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "agentcore deploy" in stdout


class TestRuntimeHHGTTG:
    """Hitchhiker's Guide theme validation (no AWS needed)."""

    @pytest.mark.hhgttg
    def test_the_answer(self):
        from tests.hhgttg import THE_ANSWER
        assert THE_ANSWER == 42

    @pytest.mark.hhgttg
    def test_deep_thought_quote_mentions_42(self):
        from tests.hhgttg import DEEP_THOUGHT_QUOTE
        assert "Forty-two" in DEEP_THOUGHT_QUOTE

    @pytest.mark.hhgttg
    def test_deep_thought_banner_renders(self):
        from tests.hhgttg import deep_thought_banner
        banner = deep_thought_banner()
        assert "DEEP THOUGHT" in banner
        assert "Forty-two" in banner
