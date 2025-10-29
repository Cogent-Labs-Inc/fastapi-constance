![🚀 Banner](https://raw.githubusercontent.com/Cogent-Labs-Inc/fastapi-constance/develop/assets/fastAPI_constance_banner.png)

# FastAPI Constance

**FastAPI Constance** is a dynamic configuration management system for FastAPI, inspired by Django Constance.
It allows developers to define application settings in code, store them in the database, and access them easily.
The system ensures type safety, supports Redis-based caching, and provides admin panel integration for managing configurations.

> ⚠️ **Note:** FastAPI Constance only supports **SQLAdmin** and **SQLAlchemy** with **asynchronous sessions** (`AsyncSession`).

## ✨ Features

- **Type-safe configuration**: Supports `int`, `float`, `str`, and `bool` types.
- **Dynamic configuration management**: Define settings in Python code and sync them with the database.
- **Admin panel integration**: Compatible with SQLAdmin for managing configurations.
- **Global wrapper**: Access settings easily via `constance_config.FEATURE_FLAG`.
- **Redis caching**: Shared, async cache ensures consistent and fast access across multiple workers.
- **Validation**: Ensures type correctness and prevents mismatches between code and database values.

## ⚡ Redis Caching

FastAPI Constance uses **Redis (async)** as its caching backend to provide high-performance, shared configuration access across all FastAPI workers.

It relies on the `redis.asyncio` client for **non-blocking I/O**, allowing your app to scale efficiently under load.
Every configuration read/write goes directly through Redis.

### ✅ Environment Variables

Set the following environment variables in your `.env` file:

```bash
REDIS_URL=redis://localhost:6379
REDIS_DB=0
```

This ensures all workers share the same configuration state in Redis.

## 📦 Installation

Install the package using pip:

```bash
pip install fastapi-constance
```

## 🚀 Usage

### 1️⃣ Initialize the Config & Lifespan

Use the `lifespan` context manager to initialize the configuration system:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_constance import constance_lifespan
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


# Example usage of Config.
USER_CONFIG = {
    "SITE_NAME": {
        "value": "Cogent Labs Portal",
        "description": "Displayed site name in the application header.",
        "type": str,
    },
    "ENABLE_SIGNUP": {
        "value": True,
        "description": "Toggle to enable or disable new user registrations.",
        "type": bool,
    },
    "DAILY_API_LIMIT": {
        "value": 5000,
        "description": "Maximum number of API calls allowed per user per day.",
        "type": int,
    },
    "DISCOUNT_RATE": {
        "value": 0.10,
        "description": "Global discount rate applied to new subscriptions.",
        "type": float,
    },
}

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Attach lifespan to initialize Constance on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session, constance_lifespan(app, session, USER_CONFIG):
        yield


app = FastAPI(lifespan=lifespan)
```

### 2️⃣ SQLAdmin Panel Integration

To use SQLAdmin for managing configurations:

```python
from sqladmin import Admin
from fastapi_constance import register_constance_admin

admin = Admin(app, engine)
register_constance_admin(admin, USER_CONFIG)  # Register config model in admin
```

### 3️⃣ Access Configuration

Access settings globally using the wrapper:

```python
from fastapi_constance import constance_config

print(await constance_config.SITE_NAME)  # Output: "Cogent Labs Portal"
print(await constance_config.ENABLE_SIGNUP)  # Output: True
print(await constance_config.DAILY_API_LIMIT)  # Output: 5000
```

> ⚠️ **Note:** Configuration values are **read-only**.
> You can **only get** values like `constance_config.SITE_NAME`, not set them manually (e.g., `constance_config.SITE_NAME = "New Name"` is **not allowed**).

## 🧱 Dependencies

- **FastAPI**: `>=0.115.0`
- **SQLAlchemy**: `>=2.0`
- **SQLModel**: `>=0.0.16`
- **SQLAdmin**: `>=0.20.0`
- **Redis**: `>=5.0.0`
- **PyTest**: `>=7.4.4`
- **PyTest Asyncio**: `>=0.23.8`

## 🤝 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code.

## 💡 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.
