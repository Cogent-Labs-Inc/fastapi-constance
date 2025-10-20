# FastAPI Constance

**FastAPI Constance** is a dynamic configuration management system for FastAPI, inspired by Django Constance.  
It allows you to define application settings in code, store them in the database, and access them easily via a global wrapper.  

**SQLAdmin integration is mandatory** for admin UI management of configurations.

---

## Features

- Define config in Python code (`CONFIG`)  
- Type-safe config (int, float, str, bool)  
- Async DB sync with SQLModel & SQLAlchemy  
- Cache config for fast access  
- Global wrapper for easy access: `constance_config.MY_SETTING`  
- SQLAdmin admin panel for managing configs  

---

## Installation

```bash
pip install fastapi-constance
