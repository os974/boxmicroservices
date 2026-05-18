"""Opérations CRUD pour le modèle Operation avec calcul automatique du résultat.

Pourquoi ce module est séparé de `main.py` : le dispatch métier
(add/sub/square + validation des opérandes) doit rester **agnostique du
transport HTTP**. `main.py` ne fait que mapper HTTP → CRUD ; `crud.py`
encapsule la logique. Conséquences pratiques :

- on peut tester `calculate_result` sans monter FastAPI (cf. `tests/`),
- on pourrait demain exposer la même logique en CLI ou en worker async sans
  duplication,
- toute évolution du contrat math (nouvelle opération, validation
  supplémentaire) se fait ici, sans toucher au routing.

Pourquoi `calculate_result` lève `ValueError` plutôt que `HTTPException` :
même raison — ne pas coupler la couche métier à FastAPI. C'est le routeur
qui traduit l'exception métier en code HTTP (400/404).
"""

from maths.mon_module import add, square, sub
from models.models import Operation
from sqlalchemy.orm import Session


def calculate_result(operation: str, a: float, b: float | None = None) -> float:
    """Dispatcher de calcul : route vers la bonne fonction math selon `operation`.

    Pourquoi un if/elif explicite plutôt qu'un dict de dispatch ou un
    `match` Python 3.10+ : choix pédagogique de lisibilité — les conditions
    de validation (`b is None`) varient selon l'opération et seraient moins
    claires dans un dict. À refactorer si on ajoute beaucoup d'opérations.

    Pourquoi la garde `if b is None` n'est pas appliquée à `square` : c'est
    une opération **unaire** par construction. `b` est délibérément ignoré
    s'il est fourni — on ne lève pas d'erreur pour ne pas pénaliser un
    client qui enverrait `b` par habitude.

    Args:
        operation (str): Type d'opération ("add", "sub", "square").
        a (float): Premier opérande.
        b (float | None): Second opérande (requis sauf pour "square").

    Returns:
        float: Résultat du calcul.

    Raises:
        ValueError: Si `operation` est inconnue, ou si `b` manque pour une
            opération binaire. Le routeur HTTP traduit ça en 400.

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
    """Insérer une nouvelle opération en BDD, avec calcul du résultat à la volée.

    Pourquoi le calcul est fait *avant* l'insert : on persiste un état
    cohérent (opérandes + résultat) en une seule transaction. Si le calcul
    échoue (`ValueError`), aucune ligne n'est créée — pas d'état partiel.

    Pourquoi le `db.refresh(...)` à la fin : récupère les valeurs générées
    par la BDD (id auto-incrémenté en particulier) pour pouvoir les renvoyer
    immédiatement au client HTTP.

    Args:
        db (Session): Session SQLAlchemy.
        operation (str): Type d'opération.
        a (float): Premier opérande.
        b (float | None): Second opérande (optionnel).

    Returns:
        Operation: l'objet ORM nouvellement créé, avec `id` peuplé.

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
    """Mettre à jour une opération existante en recalculant son résultat.

    Pourquoi on recalcule systématiquement au lieu de laisser le client
    fournir un `result` : garantit l'invariant **résultat = f(opérande)**.
    Aucun risque d'incohérence entre les opérandes stockées et la valeur
    affichée.

    Pourquoi `ValueError` (404 côté HTTP) et non un upsert silencieux : on
    refuse de créer une ressource via PUT sans ID explicite — sémantique
    REST stricte, plus prévisible pour le client.

    Args:
        db (Session): Session SQLAlchemy.
        operation_id (int): ID de l'opération à modifier.
        operation (str): Nouveau type d'opération.
        a (float): Nouvel opérande principal.
        b (float | None): Nouvel opérande secondaire (optionnel).

    Returns:
        Operation: l'objet ORM mis à jour.

    Raises:
        ValueError: si aucune opération n'existe avec cet ID. Le routeur
            traduit ça en 404.

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
