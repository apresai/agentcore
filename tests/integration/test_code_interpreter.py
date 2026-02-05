"""
Code Interpreter Demo Tests  --  Deep Thought's Calculator

"I checked it very thoroughly," said the computer,
"and that quite definitely is the answer."

The Code Interpreter demo runs Python in a secure AWS sandbox.
We verify that actual calculations are executed and returned.
"""

import pytest
from tests.conftest import assert_success, assert_no_errors


class TestCodeInterpreter:
    """Integration tests for the Code Interpreter demo."""

    DEMO = "code-interpreter"
    TIMEOUT = 120

    SUCCESS = [
        "✓ Session started:",
        "Deep Thought",
        "✓ Session stopped",
    ]

    @pytest.mark.integration
    @pytest.mark.fast
    def test_runs_successfully(self, run_demo):
        stdout, stderr, code = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert_no_errors(stdout, stderr, code)
        assert_success(stdout, self.SUCCESS)

    @pytest.mark.integration
    @pytest.mark.fast
    def test_42_appears_in_calculations(self, run_demo):
        """Deep Thought's calculations must produce 42."""
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "42" in stdout, "The Answer (42) missing from calculation output"

    @pytest.mark.integration
    @pytest.mark.fast
    def test_session_lifecycle(self, run_demo):
        """Session must start and stop cleanly."""
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "Session started" in stdout
        assert "Session stopped" in stdout

    @pytest.mark.integration
    @pytest.mark.fast
    def test_bonus_calculation_runs(self, run_demo):
        """The bonus calculation section should execute."""
        stdout, _, _ = run_demo(self.DEMO, timeout=self.TIMEOUT)
        assert "Bonus" in stdout or "bonus" in stdout


class TestCodeInterpreterHHGTTG:
    """Theme validation (no AWS needed)."""

    @pytest.mark.hhgttg
    def test_42_calculations(self):
        from tests.hhgttg import FORTY_TWO_CALCULATIONS
        for expr, expected in FORTY_TWO_CALCULATIONS:
            result = eval(expr)
            assert result == expected, f"{expr} = {result}, expected {expected}"

    @pytest.mark.hhgttg
    def test_enough_calculations(self):
        from tests.hhgttg import FORTY_TWO_CALCULATIONS
        assert len(FORTY_TWO_CALCULATIONS) >= 5, "Need variety for Deep Thought"
