# Projet 1 : Fondations, Standardisation et Excellence Technique

Ce projet constitue la "Toolbox" (boîte à outils) de référence du cursus. L'objectif est de construire un environnement de développement professionnel, automatisé et documenté, servant de template pour tous vos futurs travaux en IA.

## 1. Structure du Template de Code

Un projet professionnel doit être organisé de manière hermétique pour garantir la collaboration et la maintenance :

```plaintext
.
├── app/                   # Code source de l'application
├── tests/                 # Tests unitaires et d'intégration (Pytest)
├── docs/                  # Documentation technique (Sphinx/Furo)
├── pyproject.toml         # Configuration centralisée des outils
├── uv.lock                # Verrouillage des dépendances (généré par uv)
├── Dockerfile             # Conteneurisation de l'application
└── README.md              # Vitrine du projet (Badges, Infos, Guide)

```
Utilisez `uv init` pour initialiser le projet et `uv add x` pour ajouter les bibliothèques.
`uv run x` (application ou test) pour executer en local.

---

## 2. Configuration Centralisée : Le Cerveau `pyproject.toml`

Plutôt que de multiplier les fichiers de configuration, nous centralisons tout dans le `pyproject.toml`. Voici les sections clés à configurer et à comprendre :

### [tool.ruff] : La Police du Code

**Ruff** est un linter et formateur ultra-rapide écrit en Rust. Il remplace Black, Isort et Flake8.

* **Pourquoi ?** Pour garantir que le code est lisible par tous et pour détecter les erreurs de logique avant l'exécution.
* **Usage terminal** : `uv run ruff check .` (vérification) et `uv run ruff format .` (correction).

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "D"] # Erreurs, Warnings, Pyflakes, Isort, Docstrings
ignore = ["D100"] # On autorise l'absence de docstring en tout début de fichier

```

### [tool.pytest.ini_options] : Le Banc de Test

**Pytest** automatise la vérification de vos fonctions.

* **Pourquoi ?** Pour s'assurer qu'une modification n'a pas cassé une fonctionnalité existante (non-régression).
* **Option `--cov`** : Mesure la "couverture", soit le pourcentage de votre code réellement testé.

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-v --cov=app --cov-report=term-missing"

```

---

## 3. Qualité et Documentation

### Docstrings et Format Google

Chaque fonction doit être documentée suivant la convention **Google**. Cela permet à Sphinx de générer automatiquement la documentation technique à partir de vos commentaires de code. Pensez à créer le dossier **`docs`**.

### Sphinx et Thème Furo/RTD

Nous générons un site web de documentation moderne (mode sombre inclus) avec **Furo** ou à l'ancienne avec **Read The Doc**.

* **Intégration dynamique** : Le contenu de votre `README.md` doit être automatiquement aspiré dans la page d'accueil de votre documentation pour éviter la duplication d'information.

---

## 4. GitHub Workflow : Collaboration et CI

### Stratégie de Branching (via VS Code)

Le développement ne se fait jamais directement sur la branche `main`.

1. Création d'une branche : `feat/nom-fonctionnalite`.
2. Développement et tests locaux.
3. On ne transfert pas l'environnement virtuel (**`.gitignore`**)
4. Ouverture d'une **Pull Request (PR)** sur GitHub.

### GitHub Actions (CI)

À chaque "Push" ou "PR" (`main`, `dev` ou `feat/nom-fonctionnalite`), un robot exécute automatiquement les étapes définies dans `.github/workflows/ci.yml` :

* Installation de l'environnement avec `uv`.
* Vérification du formatage avec `ruff`.
* Exécution des tests avec `pytest`.
* **Validation** : Si un test échoue, la fusion (merge) est bloquée.

---

## 5. Un README.md de Niveau Professionnel

Votre `README.md` est votre carte de visite. Il doit obligatoirement inclure :

1. **Badges de statut** : Affichez visuellement le succès de la CI et le pourcentage de couverture de test (Pytest-cov).
2. **Guide d'installation** : Explication claire de l'usage de `uv sync`.
3. **Contributeurs** : Liste des membres de l'équipe.
4. **Code de conduite** : Le code de conduite à respecter. 
5. **Contributing** : Comment on peut contribuer à votre repos. 
6. **Licence** : Type de licence (ex: MIT) pour définir les droits de réutilisation.

- Exemple : `![CI Status](https://github.com/USER/REPO/actions/workflows/ci.yml/badge.svg)`
- Astuce : parcourir des README.md sur GitHub par exemple [numpy](https://github.com/numpy/numpy) ou [watchtower](https://github.com/containrrr/watchtower) ou autre... 

L'ancienne mais toujours très populaire norme pour les informations supplémentaires est:

```plaintext
.
├── app/                   
├── tests/                 
├── pyproject.toml         # Gestion des dépendances (uv)
├── docs/                      
├── uv.lock                    
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── LICENSE                # fichier sans extension
```

---

## 6. Objectifs du TP (Livraisons attendues)

* [ ] **Initialisation** : Créer le projet avec `uv` et configurer le `pyproject.toml`.
* [ ] **Qualité** : Passer le linter `ruff` avec succès sur tout le projet.
* [ ] **Tests** : Atteindre au moins 80% de couverture de code avec `pytest`.
* [ ] **Doc** : Générer une documentation Furo intégrant le README.
* [ ] **Docker** : Fournir un Dockerfile fonctionnel pour l'application et sa base de données associée.
* [ ] **Automatisation** : Valider que la GitHub Action passe au "Vert" sur votre dépôt.

---

## 7. Mise en Pratique : Structure Modulaire et Conteneurisation

Pour valider votre Toolbox, vous allez construire une application structurée de manière professionnelle. L'objectif est de démontrer que votre code est testable, documenté et prêt à être déployé n'importe où grâce à Docker.

### Structure attendue du code

Votre application doit suivre scrupuleusement cette hiérarchie, vous pouvez changer les noms :

```plaintext
.
├── app/                   
│   ├── modules/           # Dossier contenant la logique métier
│   │   ├── __init__.py
│   │   └── mon_module.py  # Contient les fonctions add, sub, square, print_data
│   ├── main.py            # Point d'entrée de l'application
│   └── moncsv.csv         # Données d'entrée pour la démonstration
├── tests/                 
│   └── test_math_csv.py   # Suite de tests Pytest
├── pyproject.toml         # Gestion des dépendances (uv)
├── Dockerfile             # Recette de construction de l'image
├── docs/                      
├── uv.lock                    
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── LICENSE                # fichier sans extension
```

### Spécifications du module métier

Le fichier `mon_module.py` doit implémenter :

1. **`add(a, b)`**, **`sub(a, b)`**, **`square(a)`** : Fonctions mathématiques simples.
2. **`print_data(df)`** : Reçoit un DataFrame Pandas, l'affiche, et retourne le nombre de lignes.

Le fichier `main.py` doit importer ces fonctions, lire `moncsv.csv` via Pandas, et exécuter la logique complète.

---

## 8. Stratégie de Test Avancée avec Pytest

Un bon ingénieur ne teste pas seulement "si ça marche", il teste plusieurs scénarios de manière élégante.

### Paramétrisation

Pour la fonction `add`, vous devez utiliser le décorateur `@pytest.mark.parametrize` pour tester plusieurs cas d'un coup sans dupliquer le code :

```python
@pytest.mark.parametrize("a, b, expected", [
    (10, 2, 12),
    (20, 2, 22),
    (0, 2, 2),
])
def test_add(a, b, expected):
    assert add(a, b) == expected

```

### Utilisation des Fixtures

Pour tester la fonction `print_data`, vous ne devez pas lire le vrai fichier CSV (ce qui serait un test d'intégration lourd). Utilisez une **fixture** Pytest pour générer un DataFrame temporaire en mémoire pour vos tests.

---

## 9. Le Dockerfile : Votre environnement reproductible

Le Dockerfile est le contrat qui garantit que votre application tournera de la même manière sur votre PC, sur le PC d'un collègue ou sur un serveur Cloud.

**Consignes pour le Dockerfile :**

* Utiliser une image de base légère (ex: `python:3.11-slim`).
* Copier uniquement les fichiers nécessaires.
* Installer les dépendances via `uv` (ou via un export `requirements.txt`).
* Lancer l'application via `CMD ["python", "app/main.py"]`.

---

## 10. Automatisation Finale : `ci.yml`

Il faut à présent inclure l'intégration continu en utilisant GitHub Action.
Notez que de plus en plus, et pour ne pas polluer la racine du projet, certaines informations supplémentaires sont déplacées dans le dossier `.github`.

Afin d'être reconnu automatiquement il faut créer/déplacer les dossiers et fichiers suivant:
```plaintext
.
├── .github/                   # Dossier caché de configuration GitHub
│   ├── workflows/             # Dossier contenant les fichiers de CI
│   │   └── ci.yml             # Recette d'automatisation
│   ├── CONTRIBUTING.md        
│   └── CODE_OF_CONDUCT.md
├── app/                   
│   ├── modules/           
│   │   ├── __init__.py
```


Le fichier `.github/workflows/ci.yml` est le juge de paix. Il doit s'exécuter sur les branches `dev` (via PR) et `main`.

**Les étapes du robot :**

1. **Checkout** : Récupérer le code.
2. **Setup Python & uv** : Installer les outils.
3. **Linting** : Exécuter `ruff check .`.
4. **Tests** : Exécuter `pytest`.
5. **Audit de sécurité** : Vérifier qu'aucun **Github Secret** n'est écrit en dur dans le code.

---

### Résumé du Challenge Technique

* [ ] Votre code est-il **propre** ? (Ruff doit être vert).
* [ ] Votre code est-il **fiable** ? (Pytest doit afficher 100% de succès).
* [ ] Votre code est-il **portable** ? (`docker build` doit fonctionner du premier coup).
* [ ] Votre code est-il **documenté** ? (Les docstrings doivent être présentes pour Sphinx).

