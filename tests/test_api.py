"""Test suite for the FastAPI application and CRUD operations."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Assurez-vous d'exécuter pytest depuis la racine du projet
from app_api.main import app
from app_api.modules.connect import Base, get_db
from app_api.modules.crud import calculate_result

# --- Configuration de la Base de Données de Test ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Création des tables dans la base de test
Base.metadata.create_all(bind=engine)

# --- Override de la dépendance get_db ---
def override_get_db():
    """Provide a database session for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --- Tests de calculate_result (CRUD logic) ---

def test_calculate_result_valid():
    """Test calculate_result with valid inputs."""
    assert calculate_result("add", 1, 2) == 3
    assert calculate_result("sub", 5, 3) == 2
    assert calculate_result("square", 4) == 16

def test_calculate_result_invalid():
    """Test calculate_result with invalid inputs or missing operands."""
    with pytest.raises(ValueError, match="Addition requires two operands."):
        calculate_result("add", 1, None)
    with pytest.raises(ValueError, match="Subtraction requires two operands."):
        calculate_result("sub", 1, None)
    with pytest.raises(ValueError, match="Unknown operation 'invalid'."):
        calculate_result("invalid", 1, 1)

# --- Tests Unitaires de l'API ---

def test_read_root():
    """Vérifie que l'API démarre et que la route racine répond."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running"}

def test_create_operation_success():
    """Vérifie l'insertion d'une opération valide."""
    response = client.post(
        "/data/",
        params={"operation": "add", "a": 10.0, "b": 2.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "add"
    assert data["a"] == 10.0
    assert data["b"] == 2.0
    assert data["result"] == 12.0
    assert "id" in data

def test_create_operation_error():
    """Vérifie le comportement en cas d'erreur d'opération (ex: paramètre manquant)."""
    # Addition sans paramètre b
    response = client.post(
        "/data/",
        params={"operation": "add", "a": 10.0}
    )
    assert response.status_code == 400
    assert "detail" in response.json()

def test_list_operations():
    """Vérifie la récupération de la liste des opérations."""
    # S'assurer qu'il y a au moins une donnée
    client.post("/data/", params={"operation": "square", "a": 5.0})

    response = client.get("/data/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_update_operation_success():
    """Vérifie la mise à jour d'une opération existante."""
    # D'abord on crée
    resp_create = client.post(
        "/data/", params={"operation": "add", "a": 1, "b": 1}
    )
    op_id = resp_create.json()["id"]

    # Ensuite on met à jour
    response = client.put(
        f"/data/{op_id}",
        params={"operation": "sub", "a": 10, "b": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "sub"
    assert data["a"] == 10
    assert data["b"] == 5
    assert data["result"] == 5

def test_update_operation_not_found():
    """Vérifie l'erreur 404 lors de la mise à jour d'un ID inexistant."""
    response = client.put(
        "/data/9999",
        params={"operation": "add", "a": 1, "b": 1}
    )
    assert response.status_code == 404

def test_delete_operation_success():
    """Vérifie la suppression d'une opération."""
    # Création
    resp_create = client.post("/data/", params={"operation": "square", "a": 3})
    op_id = resp_create.json()["id"]

    # Suppression
    response = client.delete(f"/data/{op_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Operation deleted"}

    # Vérification qu'elle n'est plus là
    resp_list = client.get("/data/")
    ids = [op["id"] for op in resp_list.json()]
    assert op_id not in ids

def test_delete_operation_not_found():
    """Vérifie l'erreur 404 lors de la suppression d'un ID inexistant."""
    response = client.delete("/data/9999")
    assert response.status_code == 404
