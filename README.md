# py-qwop

Eine physikbasierte Python-Adaption des legendären Spielklassikers **QWOP**, umgesetzt mit **PySide6** und der 2D-Physik-Engine **Pymunk** (Chipmunk2D).

---

## 🏃 Steuerung & Spielziel

Steuere die einzelnen Muskelpartien des Athleten, um 100 Meter auf der Tartanbahn zurückzulegen und in die Weitsprung-Sandgrube zu springen – ohne mit Kopf oder Oberkörper auf den Boden zu stürzen!

| Taste | Aktion | Beschreibung |
| --- | --- | --- |
| **Q** | Rechter Oberschenkel vor / Linker zurück | Zieht den rechten Oberschenkel nach vorn und drückt den linken nach hinten |
| **W** | Linker Oberschenkel vor / Rechter zurück | Zieht den linken Oberschenkel nach vorn und drückt den rechten nach hinten |
| **O** | Rechter Unterschenkel beugen / Links strecken | Winkelt das rechte Knie an und streckt das linke Bein durch |
| **P** | Linker Unterschenkel beugen / Rechts strecken | Winkelt das linke Knie an und streckt das rechte Bein durch |
| **R** | Neustart | Sofortiger Neustart an der Startlinie |
| **ESC** | Pause | Öffnet das Pausenmenü |
| **F11** | Vollbild / Fenster | Schaltet nahtlos zwischen Vollbild- und Fenstermodus um |

> **Hinweis:** Alle Tastenbelegungen können im Menü unter *Steuerung & Einstellungen* frei angepasst werden!

---

## ✨ Features

- **Gelenk- und Ragdoll-Physik mit Pymunk**: Authentisches Mehrkörper-Modell (Kopf, Rumpf, Oberschenkel, Unterschenkel, Füße, Arme) mit Muskelmotoren, Gelenkanschlägen und Reibung.
- **100m-Olympia-Strecke**:
  - Detaillierte Tartanbahn mit Meter-Markierungen alle 1m, 5m und 10m.
  - **Die 50m-Hürde**: Physikalisches Hindernis, das umgestoßen oder übersprungen werden kann.
  - **100m-Ziellinie & Sandgrube**: Golden glänzende Weitsprunggrube ab 100m inklusive Zielflaggen und Konfetti-Explosion.
- **Ghost-Runner (Schattenläufer)**: Zeichnet die Bewegungen des bisherigen Rekordlaufs auf und blendet ihn als transparenten Geistläufer ein.
- **Vollständiges Menü- & Scoreboard-System**:
  - Startmenü mit Rekordübersicht (beste Weite, 100m-Bestzeit, Gesamtläufe).
  - Digitales In-Game-HUD mit Live-Distanz, Stoppuhr, Geschwindigkeitsanzeige und interaktiver QWOP-Tastenbeleuchtung.
  - Pause-Overlay und Game-Over- / Sieges-Dialoge mit Statistiken.
  - Einstellungsmenü für Keybindings und Ghost-Runner-Toggle.
- **Partikelsystem**: Staubwolken beim Auftreten, Sandaufwirbelungen und Konfetti-Regen beim Zieleinlauf.
- **Vollbild & Fenstermodus**: Umschaltbar per Taste `F11` oder Menü-Button.
- **Persistenz**: Lokale Speicherung der Highscores, Einstellungen und Ghost-Posen in `save_data.json` und `best_ghost.json`.

---

## 🛠️ Voraussetzungen & Installation

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)**

```bash
# Abhängigkeiten installieren
uv sync --all-groups

# Spiel starten
uv run python -m py_qwop
```

---

## 🧪 Tests & Code-Qualität

```bash
# Tests ausführen
uv run pytest -v

# Linter ausführen
uv run ruff check .
```

---

## 📁 Projektstruktur

```text
py-qwop/
├── src/
│   └── py_qwop/
│       ├── __init__.py           # Paketinitialisierung & main()
│       ├── __main__.py           # CLI-Einstiegspunkt
│       ├── config.py             # Physikalische Konstanten, Skalierung & Farben
│       ├── storage.py            # Highscore-, Einstellungs- & Ghost-Persistenz
│       ├── physics/
│       │   ├── ragdoll.py        # Humanoid-Ragdoll mit Muskelmotoren
│       │   ├── track.py          # Tartanbahn, 50m-Hürde & Sandgrube
│       │   └── world.py          # Pymunk Space, Sub-Stepping & Kollisionen
│       ├── render/
│       │   ├── camera.py         # 2D-Kamera mit dynamischem Tracking
│       │   ├── background.py     # Parallaxe-Stadion, Tribünen & Hürde
│       │   ├── ragdoll_renderer.py # Läufer-Visuals, Z-Ordering & Ghost
│       │   └── particles.py      # Staub-, Sand- und Konfetti-Partikel
│       └── ui/
│           ├── game_widget.py    # 60 FPS Game-Loop & Canvas
│           ├── hud.py            # Scoreboard & interaktive Tastenanzeige
│           ├── main_menu.py      # Hauptmenü mit Rekorden & Navigation
│           ├── main_window.py    # QMainWindow mit Vollbild-Unterstützung
│           ├── pause_overlay.py  # Pausenmenü (ESC)
│           ├── game_over_dialog.py # Zusammenfassung & Rekordanzeige
│           └── settings_dialog.py # Tastenbelegung & Ghost-Einstellungen
├── tests/
│   ├── test_camera.py
│   ├── test_particles.py
│   ├── test_physics.py
│   ├── test_storage.py
│   └── test_ui.py
├── .github/workflows/ci.yml
├── pyproject.toml
└── README.md
```
