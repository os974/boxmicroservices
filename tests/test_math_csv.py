"""Test suite for mathematical operations and DataFrame utilities."""

import pandas as pd
import pytest

from app_api.maths.mon_module import add, compute_result, print_data, square, sub


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (3, 5, 8),
        (10, 2, 12),
        (0, 0, 0),
        (-1, 1, 0),
    ],
)
def test_add(a, b, expected):
    """Test the add function with multiple input values."""
    assert add(a, b) == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (6, 3, 3),
        (10, 5, 5),
        (0, 2, -2),
        (-5, -5, 0),
    ],
)
def test_sub(a, b, expected):
    """Test the sub function with multiple input values."""
    assert sub(a, b) == expected


@pytest.mark.parametrize(
    "a, expected",
    [
        (2, 4),
        (5, 25),
        (0, 0),
        (-3, 9),
    ],
)
def test_square(a, expected):
    """Test the square function."""
    assert square(a) == expected


@pytest.mark.parametrize(
    "operation, a, b, expected",
    [
        ("add", 10, 5, 15),
        ("sub", 10, 5, 5),
        ("square", 4, None, 16),
    ],
)
def test_compute_result_success(operation, a, b, expected):
    """Test compute_result with supported operations."""
    assert compute_result(operation, a, b) == expected


def test_compute_result_invalid_operation():
    """Test compute_result with an unsupported operation."""
    with pytest.raises(ValueError, match="Unsupported operation: invalid"):
        compute_result("invalid", 1, 2)


@pytest.fixture
def sample_dataframe():
    """Provide a temporary DataFrame for testing."""
    return pd.DataFrame(
        {
            "operation": ["add", "sub", "square", "add", "square"],
            "a": [1, 5, 3, 0, -2],
            "b": [2, 1, None, None, None],
        }
    )


def test_print_data(sample_dataframe):
    """Test that print_data returns the correct number of rows."""
    rows = print_data(sample_dataframe)
    assert rows == len(sample_dataframe)


def test_operations_with_nan_and_zero(capsys):
    """Test handling of None/NaN values and zero in operations."""
    df = pd.DataFrame(
        {
            "operation": ["add", "sub", "square", "add", "sub"],
            "a": [1, 0, 4, 0, -3],
            "b": [None, None, None, 5, 0],
        }
    )

    # execute operations and capture printed output
    print_data(df)
    captured = capsys.readouterr()
    # check key output lines
    assert "add" in captured.out
    assert "sub" in captured.out
    assert "square" in captured.out


def test_combined_operations(sample_dataframe, capsys):
    """Test executing all operations in a DataFrame."""
    print_data(sample_dataframe)
    captured = capsys.readouterr()

    # verify that output is produced
    assert "add" in captured.out
    assert "sub" in captured.out
    assert "square" in captured.out
