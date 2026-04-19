"""Unit tests for calculator module."""

import pytest
from src.calculator import Calculator


class TestCalculator:
    """Test calculator operations."""

    def setup_method(self):
        """Set up calculator for each test."""
        self.calc = Calculator()

    def test_add(self):
        """Test addition."""
        assert self.calc.add(2, 3) == 5

    def test_subtract(self):
        """Test subtraction."""
        assert self.calc.subtract(5, 3) == 2

    def test_multiply(self):
        """Test multiplication."""
        assert self.calc.multiply(4, 5) == 20

    def test_divide(self):
        """Test division."""
        assert self.calc.divide(10, 2) == 5

    def test_divide_by_zero(self):
        """Test division by zero raises error."""
        with pytest.raises(ValueError):
            self.calc.divide(10, 0)
