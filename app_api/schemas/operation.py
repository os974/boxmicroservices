"""Schémas Pydantic pour le transport HTTP des opérations.

Pourquoi ce module est séparé de `models/models.py` :
- `models/` = persistance (SQLAlchemy, schéma BDD)
- `schemas/` = contrat API (Pydantic, validation entrée/sortie HTTP)

Les deux sont libres d'évoluer séparément : on peut ajouter un champ
calculé côté `OperationRead` sans toucher au schéma BDD, ou ajouter un
champ interne en BDD sans l'exposer dans l'API. Pattern recommandé par
FastAPI.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class OperationCreate(BaseModel):
    """Payload accepté pour POST /v1/data/ et PUT /v1/data/{id}.

    Pourquoi `Literal[...]` plutôt qu'un simple `str` :
    Pydantic refusera automatiquement toute valeur hors liste en 422
    (validation au bord). Avant ce schéma, une opération inconnue
    n'était détectée qu'au moment du dispatch métier dans
    `crud.calculate_result` → 400. Maintenant l'erreur est captée plus
    tôt et son message est plus précis pour le client.

    Pourquoi `b` reste optionnel (None par défaut) :
    `square` est unaire — la cohérence "binaire requiert b" est gardée
    dans `crud.calculate_result` (raison: même garde côté CLI / futur
    worker, pas seulement HTTP).
    """

    operation: Literal["add", "sub", "square"]
    a: float
    b: float | None = None


class OperationRead(BaseModel):
    """Réponse renvoyée par les endpoints qui retournent une opération.

    Pourquoi `from_attributes=True` : permet à FastAPI de sérialiser
    directement un objet SQLAlchemy (`Operation`) sans passer par un
    sérialiseur manuel. Ça remplace la fonction `serialize_operation`
    qui existait avant.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    operation: str
    a: float
    b: float | None
    result: float | None
