# py-qwop

A python game adaptation of the game qwop.

## Voraussetzungen

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

- Qt 6 (wird automatisch über uv installiert)


## Setup

```bash
uv sync
uv run python -m py_qwop
```

## Framework

Dieses Projekt verwendet **PySide6**.

## Projektstruktur

```
py-qwop/
├── src/
│   └── py_qwop/
│       ├── __init__.py
│       ├── __main__.py
│       └── ui/
│           └── main_window.py
├── tests/
├── pyproject.toml
└── README.md
```