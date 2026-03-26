"""Business logic module containing basic mathematical operations.

This module provides functions to perform simple mathematical operations
(addition, subtraction, square) and utilities for working with pandas
DataFrames.

It also exposes a helper function to compute an operation dynamically
based on its name.
"""

from typing import Union

import pandas as pd

Number = Union[int, float]


def add(a: Number, b: Number) -> Number:
    """Add two numbers.

    Args:
        a (Number): First number.
        b (Number): Second number.

    Returns:
        Number: Sum of a and b.

    """
    return a + b


def sub(a: Number, b: Number) -> Number:
    """Subtract two numbers.

    Args:
        a (Number): First number.
        b (Number): Second number.

    Returns:
        Number: Result of a minus b.

    """
    return a - b


def square(a: Number) -> Number:
    """Return the square of a number.

    Args:
        a (Number): Input number.

    Returns:
        Number: Square of a.

    """
    return a * a


def compute_result(operation: str, a: Number, b: Number | None = None) -> Number:
    """Compute the result of a mathematical operation.

    This function acts as a dispatcher that selects the correct
    mathematical function depending on the operation name.

    Supported operations:
        - "add"
        - "sub"
        - "square"

    Args:
        operation (str): Name of the operation to execute.
        a (Number): First operand.
        b (Number | None): Second operand (optional for square).

    Returns:
        Number: Result of the operation.

    Raises:
        ValueError: If the operation name is not supported.

    """
    if operation == "add":
        return add(a, b)

    elif operation == "sub":
        return sub(a, b)

    elif operation == "square":
        return square(a)

    else:
        raise ValueError(f"Unsupported operation: {operation}")


def print_data(df: pd.DataFrame) -> int:
    """Print a DataFrame and return the number of rows.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        int: Number of rows in the DataFrame.

    """
    print(df)
    return len(df)
