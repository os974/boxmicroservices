"""CRUD operations for the Operation model with automatic result calculation.

Provides functions to insert, retrieve, update, and delete operations from the database.
"""

from maths.mon_module import add, square, sub
from models.models import Operation
from sqlalchemy.orm import Session


def calculate_result(operation: str, a: float, b: float | None = None) -> float:
    """Calculate the result of a mathematical operation.

    Args:
        operation (str): Operation type ("add", "sub", "square").
        a (float): First operand.
        b (float | None): Second operand (optional for "square").

    Returns:
        float: Result of the operation.

    """
    if operation == "add":
        if b is None:
            raise ValueError("Addition requires two operands.")
        return add(a, b)
    elif operation == "sub":
        if b is None:
            raise ValueError("Subtraction requires two operands.")
        return sub(a, b)
    elif operation == "square":
        return square(a)
    else:
        raise ValueError(f"Unknown operation '{operation}'.")


def create_data(
    db: Session, operation: str, a: float, b: float | None = None
) -> Operation:
    """Insert a new operation into the database with computed result.

    Args:
        db (Session): Database session
        operation (str): Operation type
        a (float): First operand
        b (float | None): Second operand (optional)

    Returns:
        Operation: The newly created Operation object

    """
    result = calculate_result(operation, a, b)
    db_operation = Operation(operation=operation, a=a, b=b, result=result)
    db.add(db_operation)
    db.commit()
    db.refresh(db_operation)
    return db_operation


def get_all_data(db: Session) -> list[Operation]:
    """Retrieve all operations from the database.

    Args:
        db (Session): Database session

    Returns:
        list[Operation]: List of Operation objects

    """
    return db.query(Operation).all()


def get_operation(db: Session, operation_id: int) -> Operation | None:
    """Retrieve a single operation by ID.

    Args:
        db (Session): Database session
        operation_id (int): ID of the operation

    Returns:
        Operation | None: The operation object or None if not found

    """
    return db.query(Operation).filter(Operation.id == operation_id).first()


def update_operation(
    db: Session, operation_id: int, operation: str, a: float, b: float | None = None
) -> Operation:
    """Update an existing operation and recalculate result.

    Args:
        db (Session): Database session
        operation_id (int): ID of the operation to update
        operation (str): New operation type
        a (float): New first operand
        b (float | None): New second operand (optional)

    Returns:
        Operation: Updated operation object

    Raises:
        ValueError: If operation ID does not exist

    """
    db_operation = get_operation(db, operation_id)
    if not db_operation:
        raise ValueError(f"Operation with id {operation_id} not found.")

    db_operation.operation = operation
    db_operation.a = a
    db_operation.b = b
    db_operation.result = calculate_result(operation, a, b)
    db.commit()
    db.refresh(db_operation)
    return db_operation


def delete_operation(db: Session, operation_id: int) -> bool:
    """Delete an operation from the database.

    Args:
        db (Session): Database session
        operation_id (int): ID of the operation to delete

    Returns:
        bool: True if deleted, False if not found

    """
    db_operation = get_operation(db, operation_id)
    if not db_operation:
        return False
    db.delete(db_operation)
    db.commit()
    return True
