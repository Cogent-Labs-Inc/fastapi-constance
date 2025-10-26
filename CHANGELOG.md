# Changelog

All notable changes to **fastapi-constance** will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## 0.0.1

### Release Information

- **Initial Release** of **fastapi-constance** 🎉

### Overview

`fastapi-constance` is a lightweight configuration management layer for **FastAPI**, inspired by Django Constance.
It allows developers to manage dynamic configuration settings directly from the admin interface while keeping values synced in the application cache.

### Features

- 🔧 **Dynamic Configuration Management** — Define and update app settings at runtime without redeploying.
- ⚙️ **Admin Integration** — Manage configurations directly through the FastAPI admin panel.
- 🧠 **Automatic Cache Sync** — Ensures updated values are immediately reflected in the cache.
- 🔄 **Async Lifespan Context** — Provides a simple context manager for integrating configuration during app startup and shutdown.
- 🗄️ **Database-Backed Settings** — Stores configuration data persistently using SQLAlchemy.
- 🧩 **Type-Safe Values** — Automatically casts configuration values to their defined types.
