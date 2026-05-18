"""Point d'entrée de l'API FastAPI.

Pourquoi ce fichier ne contient *que* du routing : la logique métier
(calculs, validation, accès BDD) est déléguée à `modules/crud.py`. Cette
séparation permet de tester la logique sans monter HTTP et de remplacer
demain FastAPI par un autre transport sans réécrire la couche métier.

Pourquoi un `APIRouter` avec préfixe `/v1` :
- versioning explicite de l'API (pratique attendue en micro-services) ;
- permet d'ajouter `/v2/` plus tard sans casser les clients existants ;
- regroupe tous les endpoints "data" sous un seul `tags=["operations"]`
  dans la doc Swagger.
"""

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from modules.connect import get_db
from modules.crud import (
    create_data,
    delete_operation,
    get_all_data,
    update_operation,
)
from schemas.operation import OperationCreate, OperationRead
from sqlalchemy.orm import Session

# Pourquoi plus de `Base.metadata.create_all(...)` ici : la création/évolution
# du schéma est désormais gérée par Alembic. Le conteneur Docker exécute
# `alembic upgrade head` avant `uvicorn` (cf. Dockerfile). En dev local
# hors Docker : lancer `cd app_api && uv run alembic upgrade head` une fois
# avant `uvicorn main:app`.

app = FastAPI(title="Box Microservices API", version="1.0.0")


@app.get("/")
def read_root():
    """Endpoint racine — sanity check rapide hors versioning."""
    return {"message": "API is running"}


# Pourquoi un router monté sous /v1 plutôt que des décorateurs directs :
# regroupe le versioning, les tags Swagger et les dépendances communes
# (par exemple un futur `Depends(verify_api_key)`) à un seul endroit.
router = APIRouter(prefix="/v1/data", tags=["operations"])


@router.post("/", response_model=OperationRead)
def add_operation(payload: OperationCreate, db: Session = Depends(get_db)):
    """Insérer une nouvelle opération mathématique.

    Pourquoi attraper `ValueError` → 400 : la couche `crud` lève des
    `ValueError` métier (opérande manquant pour add/sub). La validation
    du *type* d'opération est désormais faite par Pydantic (cf. `Literal`
    dans `OperationCreate`) — une opération inconnue est rejetée en 422
    avant même d'arriver ici.
    """
    try:
        return create_data(db, payload.operation, payload.a, payload.b)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[OperationRead])
def list_operations(db: Session = Depends(get_db)):
    """Lister toutes les opérations stockées."""
    return get_all_data(db)


@router.put("/{operation_id}", response_model=OperationRead)
def update_operation_endpoint(
    operation_id: int,
    payload: OperationCreate,
    db: Session = Depends(get_db),
):
    """Mettre à jour une opération existante.

    Limite connue : si l'erreur vient en réalité du calcul (`b is None`
    pour add/sub), on renvoie aussi 404, ce qui est inexact. À distinguer
    proprement quand on aura des exceptions métier typées
    (`OperationNotFound` vs `InvalidOperation`).
    """
    try:
        return update_operation(
            db, operation_id, payload.operation, payload.a, payload.b
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{operation_id}")
def delete_operation_endpoint(operation_id: int, db: Session = Depends(get_db)):
    """Supprimer une opération par son ID."""
    success = delete_operation(db, operation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Operation not found")
    return {"message": "Operation deleted"}


app.include_router(router)
