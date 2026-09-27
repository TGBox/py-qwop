"""Main gameplay widget driving the 60 FPS physics loop, rendering, input, and game state."""

import time
from typing import Any

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QKeySequence, QPainter, QPaintEvent
from PySide6.QtWidgets import QWidget

from py_qwop.config import TARGET_FPS
from py_qwop.physics.world import PhysicsWorld
from py_qwop.render.background import StadiumRenderer
from py_qwop.render.camera import Camera
from py_qwop.render.particles import ParticleSystem
from py_qwop.render.ragdoll_renderer import RagdollRenderer
from py_qwop.storage import STORAGE
from py_qwop.ui.game_over_dialog import GameOverDialog
from py_qwop.ui.hud import InGameHUD
from py_qwop.ui.pause_overlay import PauseOverlay


class GameWidget(QWidget):
    """Interactive game canvas simulating QWOP runner physics and rendering."""

    main_menu_requested = Signal()
    toggle_fullscreen_requested = Signal()

    STATE_PLAYING = "PLAYING"
    STATE_PAUSED = "PAUSED"
    STATE_CRASHED = "CRASHED"
    STATE_VICTORY = "VICTORY"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

        # Core subsystems
        self.camera = Camera(self.width(), self.height())
        self.world = PhysicsWorld()
        self.stadium = StadiumRenderer()
        self.ragdoll_renderer = RagdollRenderer()
        self.particles = ParticleSystem()
        self.hud = InGameHUD()

        # Overlays
        self.pause_overlay = PauseOverlay(self)
        self.pause_overlay.hide()
        self.pause_overlay.resume_requested.connect(self.resume_game)
        self.pause_overlay.restart_requested.connect(self.restart_game)
        self.pause_overlay.main_menu_requested.connect(self._to_main_menu)

        self.game_over_dialog = GameOverDialog(self)
        self.game_over_dialog.hide()
        self.game_over_dialog.restart_requested.connect(self.restart_game)
        self.game_over_dialog.main_menu_requested.connect(self._to_main_menu)

        # Physics event hooks
        self.world.on_crash = self._handle_crash
        self.world.on_victory = self._handle_victory
        self.world.on_footstep = self._handle_footstep

        # Game state
        self.state = self.STATE_PLAYING
        self.keys_pressed: dict[str, bool] = {
            "thigh_q": False,
            "thigh_w": False,
            "calf_o": False,
            "calf_p": False,
        }
        self.key_bindings: dict[str, int] = {}
        self.key_names: dict[str, str] = {}
        self.is_fullscreen: bool = False

        # Ghost runner playback and recording
        self.ghost_enabled: bool = True
        self.ghost_frames: list[dict[str, Any]] | None = None
        self.recorded_run: list[dict[str, Any]] = []
        self.ghost_record_timer: float = 0.0

        # Timing
        self.last_time = time.perf_counter()
        self.anim_time = 0.0

        # 60 FPS Game Loop Timer
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self._tick)
        self.game_timer.start(int(1000 / TARGET_FPS))

        self.reload_config()

    def reload_config(self) -> None:
        """Reload key bindings and ghost runner preferences."""
        data = STORAGE.load_data()
        self.key_bindings = data.get("key_bindings", {})
        self.ghost_enabled = data.get("settings", {}).get("ghost_runner_enabled", True)
        self.ghost_frames = STORAGE.load_ghost() if self.ghost_enabled else None

        # Build human-readable key names for HUD buttons
        self.key_names = {
            action: QKeySequence(code).toString()
            for action, code in self.key_bindings.items()
        }

    def start_new_game(self) -> None:
        """Reset runner, obstacles, and start fresh."""
        self.reload_config()
        self.restart_game()

    def restart_game(self) -> None:
        """Reset runner state and resume playing immediately."""
        self.pause_overlay.hide()
        self.game_over_dialog.hide()

        self.world.reset()
        self.camera.reset()
        self.particles.clear()
        self.recorded_run.clear()
        self.ghost_record_timer = 0.0
        self.anim_time = 0.0
        self.keys_pressed = {k: False for k in self.keys_pressed}
        self.state = self.STATE_PLAYING
        self.last_time = time.perf_counter()
        self.setFocus()

    def pause_game(self) -> None:
        """Pause active simulation and display pause overlay."""
        if self.state == self.STATE_PLAYING:
            self.state = self.STATE_PAUSED
            self.pause_overlay.setGeometry(self.rect())
            self.pause_overlay.show()
            self.pause_overlay.raise_()

    def resume_game(self) -> None:
        """Resume simulation from pause."""
        if self.state == self.STATE_PAUSED:
            self.pause_overlay.hide()
            self.state = self.STATE_PLAYING
            self.last_time = time.perf_counter()
            self.setFocus()

    def _to_main_menu(self) -> None:
        """Navigate back to the main start menu."""
        self.pause_overlay.hide()
        self.game_over_dialog.hide()
        self.main_menu_requested.emit()

    def _handle_crash(self) -> None:
        """Triggered when runner head or chest hits ground."""
        if self.state != self.STATE_PLAYING:
            return

        self.state = self.STATE_CRASHED
        dist = self.world.runner.get_progress_x()
        is_new_rec = STORAGE.update_record(dist, self.world.time_elapsed)

        # If achieved a record run, save ghost
        if is_new_rec and len(self.recorded_run) > 10:
            STORAGE.save_ghost(self.recorded_run)

        self.game_over_dialog.set_results(
            is_victory=False,
            distance=dist,
            time_sec=self.world.time_elapsed,
            is_new_record=is_new_rec,
        )
        self.game_over_dialog.setGeometry(self.rect())
        self.game_over_dialog.show()
        self.game_over_dialog.raise_()

    def _handle_victory(self) -> None:
        """Triggered when runner crosses 100m finish line."""
        if self.state != self.STATE_PLAYING:
            return

        self.state = self.STATE_VICTORY
        dist = self.world.runner.get_progress_x()
        is_new_rec = STORAGE.update_record(dist, self.world.time_elapsed)

        # Spawn festive victory confetti
        self.particles.spawn_confetti(100.0, 3.2, count=140)

        # Save victorious run as ghost
        if len(self.recorded_run) > 10:
            STORAGE.save_ghost(self.recorded_run)

        self.game_over_dialog.set_results(
            is_victory=True,
            distance=dist,
            time_sec=self.world.time_elapsed,
            is_new_record=is_new_rec,
        )
        self.game_over_dialog.setGeometry(self.rect())
        self.game_over_dialog.show()
        self.game_over_dialog.raise_()

    def _handle_footstep(self, x: float, y: float, is_sand: bool) -> None:
        """Spawn dust particle effect when foot hits track or sand."""
        self.particles.spawn_foot_dust(x, y, is_sand)

    def _tick(self) -> None:
        """Main game loop tick called at 60 FPS."""
        now = time.perf_counter()
        dt = min(1.0 / 30.0, max(0.001, now - self.last_time))
        self.last_time = now

        if self.state in (self.STATE_PLAYING, self.STATE_CRASHED, self.STATE_VICTORY):
            # Step physics (even when crashed so ragdoll settles naturally)
            self.world.update(dt, self.keys_pressed)
            self.anim_time += dt

            # Update camera
            cx, cy = self.world.runner.get_center_position()
            vx, _ = self.world.runner.get_velocity()
            self.camera.update(cx, cy, vx, dt)

            # Record ghost frames during active play (20 times per second)
            if self.state == self.STATE_PLAYING:
                self.ghost_record_timer += dt
                if self.ghost_record_timer >= 0.05:
                    self.ghost_record_timer = 0.0
                    frame = self.world.runner.capture_pose()
                    frame["t"] = round(self.world.time_elapsed, 2)
                    self.recorded_run.append(frame)

        # Update visual particles
        self.particles.update(dt)

        # Request paint
        self.update()

    def _get_current_ghost_frame(self) -> dict[str, Any] | None:
        """Find ghost pose frame matching current elapsed time."""
        if not self.ghost_enabled or not self.ghost_frames:
            return None

        current_t = self.world.time_elapsed
        # Binary or sequential search through ghost frames
        best_frame = None
        for frame in self.ghost_frames:
            if frame.get("t", 0.0) <= current_t:
                best_frame = frame
            else:
                break
        return best_frame

    def paintEvent(self, event: QPaintEvent) -> None:
        """Render all visual layers to the widget."""
        painter = QPainter(self)

        # 1. Environment & Olympic Stadium
        self.stadium.render(
            painter=painter,
            camera=self.camera,
            hurdle_body=self.world.track.hurdle_body,
            anim_time=self.anim_time,
        )

        # 2. Runner & Ghost Runner
        ghost_frame = self._get_current_ghost_frame()
        self.ragdoll_renderer.render(
            painter=painter,
            camera=self.camera,
            runner=self.world.runner,
            ghost_frame=ghost_frame,
        )

        # 3. Particle System (Dust, Sand, Confetti)
        self.particles.render(painter, self.camera)

        # 4. In-Game HUD (Scores, Timer, Key Indicators)
        vx, _ = self.world.runner.get_velocity()
        speed_kmh = max(0.0, vx * 3.6)
        dist = self.world.runner.get_progress_x()

        self.hud.render(
            painter=painter,
            width=self.width(),
            height=self.height(),
            distance=dist,
            time_elapsed=self.world.time_elapsed,
            speed_kmh=speed_kmh,
            keys_pressed=self.keys_pressed,
            key_names=self.key_names,
            is_fullscreen=self.is_fullscreen,
        )

    def resizeEvent(self, event) -> None:
        """Handle resize to adjust camera viewport and dialog layouts."""
        super().resizeEvent(event)
        self.camera.resize(self.width(), self.height())
        if self.pause_overlay.isVisible():
            self.pause_overlay.setGeometry(self.rect())
        if self.game_over_dialog.isVisible():
            self.game_over_dialog.setGeometry(self.rect())

    def keyPressEvent(self, event) -> None:
        """Handle user keyboard presses."""
        key = event.key()

        # Check action bindings
        if key == self.key_bindings.get("thigh_q"):
            self.keys_pressed["thigh_q"] = True
        elif key == self.key_bindings.get("thigh_w"):
            self.keys_pressed["thigh_w"] = True
        elif key == self.key_bindings.get("calf_o"):
            self.keys_pressed["calf_o"] = True
        elif key == self.key_bindings.get("calf_p"):
            self.keys_pressed["calf_p"] = True
        elif key == self.key_bindings.get("restart"):
            self.restart_game()
        elif key == self.key_bindings.get("pause"):
            if self.state == self.STATE_PLAYING:
                self.pause_game()
            elif self.state == self.STATE_PAUSED:
                self.resume_game()
        elif key == self.key_bindings.get("fullscreen"):
            self.toggle_fullscreen_requested.emit()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event) -> None:
        """Handle key releases."""
        key = event.key()

        if key == self.key_bindings.get("thigh_q"):
            self.keys_pressed["thigh_q"] = False
        elif key == self.key_bindings.get("thigh_w"):
            self.keys_pressed["thigh_w"] = False
        elif key == self.key_bindings.get("calf_o"):
            self.keys_pressed["calf_o"] = False
        elif key == self.key_bindings.get("calf_p"):
            self.keys_pressed["calf_p"] = False
        else:
            super().keyReleaseEvent(event)
