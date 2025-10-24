# FastAPI Constance

**FastAPI Constance** is a dynamic configuration management system for FastAPI, inspired by Django Constance.
It allows developers to define application settings in code, store them in the database, and access them easily via a global wrapper.

> ⚠️ **Note:** FastAPI Constance only supports **SQLAdmin** and **SQLAlchemy** with **asynchronous sessions** (`AsyncSession`).

The system ensures type safety, supports caching, and provides admin panel integration for managing configurations.
**FastAPI Constance** is a dynamic configuration management system for FastAPI, inspired by Django Constance. It allows developers to define application settings in code, store them in the database, and access them easily via a global wrapper. The system ensures type safety, supports caching, and provides admin panel integration for managing configurations.

## Features

- **Type-safe configuration**: Supports `int`, `float`, `str`, and `bool` types.
- **Dynamic configuration management**: Define settings in Python code and sync them with the database.
- **Admin panel integration**: Compatible with SQLAdmin for managing configurations.
- **Global wrapper**: Access settings easily via `constance_config.INTEGER`.
- **Caching**: Configurations are cached for fast access.
- **Validation**: Ensures type correctness and prevents mismatches between code and database values.

## Installation

Install the package using pip:

```bash
pip install fastapi-constance
```

## Usage

### 1. Initialize the Config & Lifespan

Use the `lifespan` context manager to initialize the configuration system:

```python
from fastapi import FastAPI
from fastapi_constance import lifespan
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


# USER_CONFIG is just an example; users can define it anywhere and name it anything.
USER_CONFIG = {
    "INTEGER": {
        "value": 42,
        "description": "Sample integer implementation.",
        "type": int,
    },
    "DEBUG_MODE": {
        "value": True,
        "description": "Enable debug mode.",
        "type": bool,
    },
    "FLOAT": {
        "value": 98.11,
        "description": "Sample float implementation.",
        "type": float,
    },
    "STR": {
        "value": "FastAPI Constance",
        "description": "Sample string implementation.",
        "type": str,
    },
}

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Attach lifespan to initialize Constance on startup
app = FastAPI(lifespan=lambda app: lifespan(app, AsyncSessionLocal(), USER_CONFIG))
```

### 2. SQLAdmin Panel Integration

To use SQLAdmin for managing configurations:

```python
from sqladmin import Admin
from fastapi_constance import register_constance_admin

admin = Admin(app, engine)
register_constance_admin(admin, USER_CONFIG)  # Register config model in admin
```

### 3. Access Configuration

Access settings globally using the wrapper:

```python
from fastapi_constance import constance_config

print(constance_config.INTEGER)  # Output: 42
```

> ⚠️ **Note:** Configuration values are **read-only**. You can **only get** values like `constance_config.INTEGER`, not set them manually (e.g., `constance_config.INTEGER = 50` is **not allowed**).

## Configuration Management

### Sync Settings

The `ConstanceConfigManager` ensures that settings defined in code are synchronized with the database. It validates types, updates default values, and removes stale entries.

### Wrapper

The `ConstanceConfigWrapper` provides a global interface for accessing settings. It ensures that the manager is properly configured before accessing any settings.

## Error Handling

The package includes custom exceptions for handling common issues:

- **NotSupportedTypeError**: Raised when an unsupported type is used.
- **TypeMismatchError**: Raised when a value does not match the expected type.
- **ImproperlyConfiguredError**: Raised when the configuration manager is not properly initialized.

## Dependencies

The project requires the following dependencies:

- **FastAPI**: `>=0.115.0`
- **SQLAlchemy**: `>=2.0`
- **SQLModel**: `>=0.0.16`
- **SQLAdmin**: `>=0.20.0`

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code.

## Author

**Muhammad Aoun Zaidi**
Email: zaoun123@gmail.com
GitHub: [FastAPI Constance](https://github.com/Cogent-Labs-Inc/fastapi-constance)
