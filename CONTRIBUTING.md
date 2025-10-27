# Contributing to FastAPI Constance

Thank you for your interest in contributing to **FastAPI Constance**!
This document outlines the guidelines for contributing to this Python package.

## 1. Fork and Clone the Repository

- Fork the repository to your **own GitHub account** by clicking the **“Fork”** button on
  [https://github.com/Cogent-Labs-Inc/fastapi-constance](https://github.com/Cogent-Labs-Inc/fastapi-constance).

- After forking, clone **your forked copy** of the repository to your local machine:

  ```bash
  git clone https://github.com/<your-username>/fastapi-constance.git
  cd fastapi-constance
  ```

## 2. Set Up Pre-commit Hooks

- Install pre-commit:

  ```bash
  pip install pre-commit
  ```

- Activate the pre-commit hook:

  ```bash
  pre-commit install
  ```

## 3. Create a Branch and Make Changes

1. **Create a new branch** for your contribution. Use the following naming conventions:

   - `epic/`: For large, multi-part features
   - `feat/`: For new features
   - `enh/`: For improvements / enhancements
   - `bug/`: For bug fixes
   - `hotfix/`: For urgent fixes that need to be applied directly to production

   Example:

   ```bash
   git checkout -b feat/add-new-feature
   ```

2. **Make your changes** and commit with a clear message:

   ```bash
   git commit -m "feat: add a new feature"
   ```

3. **Push your branch**:

   ```bash
   git push origin feat/add-new-feature
   ```

4. **Open a Pull Request** describing your changes.
