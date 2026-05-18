"""Modèles ORM de l'application.

Pourquoi un fichier dédié : séparer la définition du schéma persistant (ce
module) de la logique CRUD (`modules/crud.py`) et du transport HTTP
(`main.py`). Trois responsabilités → trois fichiers, ça facilite la
substitution future (ex. passage à des schémas Pydantic explicites côté API
sans toucher au modèle ORM).

Pourquoi on importe `Base` depuis `modules.connect` plutôt que de le
redéfinir ici : il ne doit exister qu'**un seul** `declarative_base()` par
application, sinon SQLAlchemy ne sait plus quelles tables créer via
`Base.metadata.create_all()`.
"""

from modules.connect import Base
from sqlalchemy import Column, Float, Integer, String


class Operation(Base):
    """Modèle ORM représentant une opération mathématique persistée.

    Pourquoi un seul table pour les 3 opérations (add/sub/square) plutôt que
    3 tables : les colonnes sont identiques (deux opérandes + un résultat),
    et le type d'opération est une simple étiquette. Une table par type
    serait du sur-design pour le périmètre actuel.

    Pourquoi `b` est nullable : `square` est unaire (un seul opérande), alors
    que `add`/`sub` sont binaires. Plutôt que d'introduire une seconde table
    ou un schéma polymorphe, on autorise `b = NULL` et la validation est
    faite côté `crud.calculate_result` (cf. garde `if b is None`).

    Pourquoi `result` est nullable : couvre un cas futur où on stockerait
    une opération sans la calculer (file d'attente, calcul différé). Pas
    utilisé aujourd'hui, mais ne coûte rien.

    Attributes:
        id (int): Clé primaire auto-incrémentée.
        operation (str): Type d'opération ("add", "sub", "square").
        a (float): Premier opérande.
        b (float | None): Second opérande, optionnel pour les opérations unaires.
        result (float | None): Résultat calculé.

    """

    __tablename__ = "operations"
    # `extend_existing=True` : nécessaire parce que pytest peut réimporter ce
    # module plusieurs fois dans la même session (conftest + tests), ce qui
    # déclencherait sinon "Table 'operations' is already defined for this
    # MetaData instance". À garder tant qu'on n'a pas isolé strictement les
    # imports de tests.
    __table_args__ = {"extend_existing": True}

    # `index=True` sur la PK : redondant avec l'index implicite de SQLAlchemy
    # sur primary_key, mais rendu explicite ici pour la lisibilité pédagogique.
    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, nullable=False)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=True)
    result = Column(Float, nullable=True)
