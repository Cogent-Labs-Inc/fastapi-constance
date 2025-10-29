  

# Contributing to FastAPI Constance

Thank you for your interest in contributing to **FastAPI Constance**!
This guide explains how to contribute effectively while maintaining consistency and code quality.

  

## 1. Fork and Clone the Repository

1. Fork the repository to your **own GitHub account** by clicking the **“Fork”** button on
   [https://github.com/Cogent-Labs-Inc/fastapi-constance](https://github.com/Cogent-Labs-Inc/fastapi-constance).

2. Clone **your forked copy** to your local machine:

   ```bash
   git clone https://github.com/<your-username>/fastapi-constance.git
   cd fastapi-constance
   ```

  

## 2. Set Up Pre-commit Hooks

To maintain consistent formatting and code quality, we use **pre-commit hooks**.

1. Install pre-commit:

   ```bash
   pip install pre-commit
   ```

2. Activate the pre-commit hook:

   ```bash
   pre-commit install
   ```

> These hooks automatically check formatting, imports, and linting before each commit.

  

## 3. Create a Branch for Your Changes

Before making changes, create a new branch following the naming conventions below:

| Type      | Description                              | Example                    |
| --------- | ---------------------------------------- | -------------------------- |
| `epic/`   | Large, multi-part features               | `epic/config-management`   |
| `feat/`   | New features                             | `feat/add-new-feature`     |
| `enh/`    | Improvements or enhancements             | `enh/improve-cache-layer`  |
| `bug/`    | Bug fixes                                | `bug/fix-redis-connection` |
| `hotfix/` | Critical fixes to be applied immediately | `hotfix/fix-env-variable`  |

Example:

```bash
git checkout -b feat/add-new-feature
```

  

## 4. Make Changes and Commit

After implementing your updates:

1. **Stage and commit** with a clear, descriptive message:

   ```bash
   git add .
   git commit -m "feat: add configuration caching mechanism"
   ```

2. **Push your branch** to your fork:

   ```bash
   git push origin feat/add-new-feature
   ```

  

## 5. Write and Run Test Cases

All new features, enhancements, and bug fixes **must include test coverage**.
FastAPI Constance uses **pytest** for testing.

### 🧩 Directory Structure

Each module in the project has its own test directory:

```
tests/
├── admin/
│   ├── test_constance_config_admin.py
│   └── conftest.py
└── ...
```

* Keep test files **inside the corresponding module directory**.
* Use descriptive file names starting with `test_`.
* Use **fixtures** in `conftest.py` to mock dependencies like Redis or database sessions.

  

### ✅ Writing Tests

* Prefix test functions with `test_`.
* Include a clear **docstring** explaining what the test validates.
* Use `pytest.mark.asyncio` for async functions.
* Mock external dependencies (e.g., Redis, database) using `AsyncMock` or `MagicMock`.
* Write both **positive** and **negative** test cases.

Example:

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_add_config_creates_entry_successfully():
    """
    Test that a new configuration entry is created successfully.
    """
    mock_cache = AsyncMock()
    ...
    await some_service.add_config("DEBUG", True)
    mock_cache.set.assert_awaited_once_with("DEBUG", True)
```

  

### 🧪 Running Tests

To run all tests:

```bash
pytest
```

To run tests for a specific module:

```bash
pytest tests/constance_config_manager/
```

To check coverage:

```bash
pytest --cov=fastapi_constance --cov-report=term-missing
```

  

## 6. Code Quality and Style

* Ensure all **pre-commit checks** pass before pushing.
* Follow **PEP 8** and **FastAPI best practices**.
* Use **type hints**, **docstrings**, and clear variable names.
* Keep functions **short, testable, and modular**.

  

## 7. Submit a Pull Request (PR)

When your feature or fix is ready:

1. Push your branch to your fork.
2. Open a **Pull Request (PR)** to the `develop` branch.
3. Include:

   * A clear summary of your change
   * Relevant issue references (e.g., `Fixes #123`)
   * Details of how the change was tested

  

## 8. Review and Merge

* Maintainers will review your PR for functionality, design, and test coverage.
* You may receive feedback — address it promptly.
* Once approved, your changes will be merged into the develop branch.

  
