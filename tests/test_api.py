"""Tests de l'application FastAPI et de la logique CRUD."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app_api.main import app
from app_api.modules.connect import Base, get_db
from app_api.modules.crud import calculate_result

# Base SQLite en mémoire + StaticPool : garde *une seule* connexion
# partagée par tous les TestClient pour que la BDD reste cohérente entre
# requêtes (sinon chaque connexion verrait sa propre :memory:).
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override de la dépendance get_db pour pointer sur la BDD en mémoire."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --- Tests calculate_result (logique métier pure, sans HTTP) ---

def test_calculate_result_valid():
    """Vérifie calculate_result avec des entrées valides."""
    assert calculate_result("add", 1, 2) == 3
    assert calculate_result("sub", 5, 3) == 2
    assert calculate_result("square", 4) == 16


def test_calculate_result_invalid():
    """Vérifie calculate_result avec entrées invalides ou opérandes manquants."""
    with pytest.raises(ValueError, match="Addition requires two operands."):
        calculate_result("add", 1, None)
    with pytest.raises(ValueError, match="Subtraction requires two operands."):
        calculate_result("sub", 1, None)
    with pytest.raises(ValueError, match="Unknown operation 'invalid'."):
        calculate_result("invalid", 1, 1)


# --- Tests HTTP : on tape sur /v1/data/ avec un body JSON ---

def test_read_root():
    """Vérifie que la racine répond toujours, hors versioning."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running"}


def test_create_operation_success():
    """Insertion d'une opération valide via body JSON."""
    response = client.post(
        "/v1/data/", json={"operation": "add", "a": 10.0, "b": 2.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "add"
    assert data["a"] == 10.0
    assert data["b"] == 2.0
    assert data["result"] == 12.0
    assert "id" in data


def test_create_operation_missing_b_for_add():
    """Add sans b : Pydantic l'accepte (b optionnel), crud lève → 400."""
    response = client.post("/v1/data/", json={"operation": "add", "a": 10.0})
    assert response.status_code == 400
    assert "detail" in response.json()


def test_create_operation_unknown_op_rejected_by_pydantic():
    """Une opération hors Literal est rejetée par Pydantic en 422 (pas 400)."""
    response = client.post(
        "/v1/data/", json={"operation": "modulo", "a": 1.0, "b": 2.0}
    )
    assert response.status_code == 422


def test_list_operations():
    """Récupération de la liste des opérations."""
    client.post("/v1/data/", json={"operation": "square", "a": 5.0})

    response = client.get("/v1/data/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_update_operation_success():
    """Mise à jour d'une opération existante."""
    resp_create = client.post(
        "/v1/data/", json={"operation": "add", "a": 1, "b": 1}
    )
    op_id = resp_create.json()["id"]

    response = client.put(
        f"/v1/data/{op_id}",
        json={"operation": "sub", "a": 10, "b": 5},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "sub"
    assert data["a"] == 10
    assert data["b"] == 5
    assert data["result"] == 5


def test_update_operation_not_found():
    """PUT sur ID inexistant → 404."""
    response = client.put(
        "/v1/data/9999", json={"operation": "add", "a": 1, "b": 1}
    )
    assert response.status_code == 404


def test_delete_operation_success():
    """Suppression d'une opération."""
    resp_create = client.post("/v1/data/", json={"operation": "square", "a": 3})
    op_id = resp_create.json()["id"]

    response = client.delete(f"/v1/data/{op_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Operation deleted"}

    resp_list = client.get("/v1/data/")
    ids = [op["id"] for op in resp_list.json()]
    assert op_id not in ids


def test_delete_operation_not_found():
    """DELETE sur ID inexistant → 404."""
    response = client.delete("/v1/data/9999")
    assert response.status_code == 404
