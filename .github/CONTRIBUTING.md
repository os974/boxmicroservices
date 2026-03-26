# Contributing Guidelines

Thank you for considering contributing to this project.

We welcome contributions that improve the codebase, documentation, or project structure.

---

## How to Contribute

### 1. Fork the repository

Create your own fork of the repository.

### 2. Create a branch

Use a descriptive branch name.

Example:

feature/add-new-operation

or

fix/csv-parsing

### 3. Install the project

```
uv sync
```

### 4. Run tests

Before submitting changes, ensure tests pass.

```
uv run pytest
```

### 5. Run linting

```
uv run ruff check
```

### 6. Submit a Pull Request

Provide:

- clear description
- motivation for the change
- related issue if applicable

---

## Code Standards

Contributors must follow:

- PEP8 style guidelines
- Ruff linting rules
- Proper docstring documentation

---

## Testing

All new features should include tests.

Coverage should not decrease significantly.

---

## Commit Messages

Use clear commit messages.

Example:

```
feat: add square operation
docs: update README
```

---

Thank you for helping improve the project.