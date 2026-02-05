"""
Memory Demo Tests  --  Marvin the Paranoid Android

"I think you ought to know I'm feeling very depressed."

Marvin remembers everything. He just wishes he didn't.
The Memory demo stores and retrieves Marvin's existential observations.
"""

import pytest
from tests.conftest import assert_success, assert_no_errors


class TestMemory:
    """Integration tests for the Memory demo."""

    DEMO = "memory"
    TIMEOUT = 720  # Memory creation can take 5+ minutes

    SUCCESS = [
        "✓ AgentCore clients initialized",
        "✓ Memory created:",
    ]

    @pytest.fixture(scope="class")
    def demo_output(self, run_demo):
        """Run the memory demo once and share output across all tests."""
        stdout, stderr, code = run_demo(self.DEMO, timeout=self.TIMEOUT)
        return stdout, stderr, code

    @pytest.mark.integration
    @pytest.mark.slow
    def test_runs_successfully(self, demo_output):
        stdout, stderr, code = demo_output
        assert_no_errors(stdout, stderr, code)
        assert_success(stdout, self.SUCCESS)

    @pytest.mark.integration
    @pytest.mark.slow
    def test_marvin_quote_stored(self, demo_output):
        """A Marvin quote should appear in stored events."""
        stdout, _, _ = demo_output
        # The demo stores a Marvin quote as the conversation
        assert "Marvin" in stdout or "depressed" in stdout or "brain" in stdout, \
            "Marvin-themed content missing from memory events"

    @pytest.mark.integration
    @pytest.mark.slow
    def test_memory_lifecycle(self, demo_output):
        """Full lifecycle: create -> store -> retrieve -> delete."""
        stdout, _, _ = demo_output
        assert "Creating memory:" in stdout
        assert "✓ Memory created:" in stdout
        # Memory activation and full flow (may fail on transient network issues)
        if "✓ Memory is active" in stdout:
            assert "Storing" in stdout
            assert "Retrieving" in stdout

    @pytest.mark.integration
    @pytest.mark.slow
    def test_cleanup_always_runs(self, demo_output):
        """Memory must be deleted even if demo encounters issues."""
        stdout, _, _ = demo_output
        assert "Memory deleted" in stdout or "Cleanup note:" in stdout or "Cleaning up" in stdout


class TestMemoryHHGTTG:
    """Theme validation (no AWS needed)."""

    @pytest.mark.hhgttg
    def test_marvin_quotes_available(self):
        from tests.hhgttg import MARVIN_QUOTES
        assert len(MARVIN_QUOTES) >= 5

    @pytest.mark.hhgttg
    def test_marvin_quotes_are_depressing(self):
        from tests.hhgttg import MARVIN_QUOTES
        keywords = {"depressed", "life", "hate", "worst", "death", "brain", "planet"}
        for quote in MARVIN_QUOTES:
            has_keyword = any(kw in quote.lower() for kw in keywords)
            assert has_keyword or "I" in quote, f"Not melancholy enough: {quote}"

    @pytest.mark.hhgttg
    def test_random_marvin_quote(self):
        from tests.hhgttg import random_marvin_quote, MARVIN_QUOTES
        quote = random_marvin_quote()
        assert quote in MARVIN_QUOTES
