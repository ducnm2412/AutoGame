# ============================================================
# AUTO GAME - Kivy Android App
# UI: Play ▶️ | Pause ⏸️ | Restart 🔄
# ============================================================

import os
os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Triangle, Rectangle, Line, Ellipse
from kivy.uix.widget import Widget
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex

from android_controller import AndroidController
from image_matcher import ImageMatcher
from bot_engine import BotEngine

# Màu sắc
BG_COLOR = get_color_from_hex("#1a1a2e")
CARD_COLOR = get_color_from_hex("#16213e")
PLAY_COLOR = get_color_from_hex("#00c853")
PAUSE_COLOR = get_color_from_hex("#ffc107")
RESTART_COLOR = get_color_from_hex("#2196f3")
STOP_COLOR = get_color_from_hex("#f44336")
TEXT_COLOR = get_color_from_hex("#e0e0e0")
LOG_BG = get_color_from_hex("#0d1117")


class PlayIcon(Widget):
    """Nút tam giác Play."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._draw, pos=self._draw)

    def _draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*PLAY_COLOR)
            cx, cy = self.center
            s = min(self.width, self.height) * 0.35
            Triangle(points=[
                cx - s * 0.5, cy - s,
                cx - s * 0.5, cy + s,
                cx + s, cy
            ])


class PauseIcon(Widget):
    """Nút 2 thanh Pause."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._draw, pos=self._draw)

    def _draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*PAUSE_COLOR)
            cx, cy = self.center
            s = min(self.width, self.height) * 0.3
            bar_w = s * 0.35
            gap = s * 0.3
            Rectangle(pos=(cx - gap - bar_w, cy - s), size=(bar_w, s * 2))
            Rectangle(pos=(cx + gap, cy - s), size=(bar_w, s * 2))


class RestartIcon(Widget):
    """Nút mũi tên tròn Restart."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._draw, pos=self._draw)

    def _draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*RESTART_COLOR)
            cx, cy = self.center
            s = min(self.width, self.height) * 0.3
            Line(circle=(cx, cy, s, 0, 300), width=dp(3))
            # Mũi tên
            Triangle(points=[
                cx + s * 0.5, cy + s * 0.6,
                cx + s * 0.9, cy + s * 0.2,
                cx + s * 0.1, cy + s * 0.2,
            ])


class ControlButton(Button):
    """Nút điều khiển với hiệu ứng."""
    def __init__(self, btn_color, **kwargs):
        super().__init__(**kwargs)
        self.btn_color = btn_color
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.background_down = ""
        self.color = TEXT_COLOR
        self.font_size = sp(16)
        self.bold = True
        self.bind(size=self._draw_bg, pos=self._draw_bg)

    def _draw_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.btn_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])


class AutoGameApp(App):
    """App chính."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = AndroidController()
        self.matcher = ImageMatcher()
        self.bot = None
        self.log_lines = []

    def build(self):
        self.title = "🌸 Auto Game"
        Window.clearcolor = BG_COLOR

        # Layout chính
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        # Header
        header = Label(
            text="🌸 Auto Game\nThế Giới Hoa Viên",
            font_size=sp(22),
            bold=True,
            color=TEXT_COLOR,
            size_hint_y=None,
            height=dp(70),
            halign="center",
        )
        header.bind(size=header.setter("text_size"))
        root.add_widget(header)

        # Status
        self.status_label = Label(
            text="⏹️ Chưa chạy",
            font_size=sp(16),
            color=get_color_from_hex("#aaaaaa"),
            size_hint_y=None,
            height=dp(30),
        )
        root.add_widget(self.status_label)

        # Stats
        self.stats_label = Label(
            text="📦 Đơn: 0  |  🌱 Farm: 0  |  ❌ Lỗi: 0",
            font_size=sp(14),
            color=get_color_from_hex("#888888"),
            size_hint_y=None,
            height=dp(25),
        )
        root.add_widget(self.stats_label)

        # Buttons row
        btn_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(60),
        )

        # Play button
        self.play_btn = ControlButton(
            btn_color=PLAY_COLOR,
            text="▶  Bắt đầu",
        )
        self.play_btn.bind(on_press=self.on_play)
        btn_row.add_widget(self.play_btn)

        # Pause button
        self.pause_btn = ControlButton(
            btn_color=PAUSE_COLOR,
            text="⏸  Tạm dừng",
        )
        self.pause_btn.bind(on_press=self.on_pause)
        btn_row.add_widget(self.pause_btn)

        # Restart button
        self.restart_btn = ControlButton(
            btn_color=RESTART_COLOR,
            text="🔄  Restart",
        )
        self.restart_btn.bind(on_press=self.on_restart)
        btn_row.add_widget(self.restart_btn)

        root.add_widget(btn_row)

        # Log area
        log_scroll = ScrollView(size_hint_y=1)
        self.log_label = Label(
            text="",
            font_size=sp(12),
            color=get_color_from_hex("#00ff88"),
            halign="left",
            valign="top",
            size_hint_y=None,
            markup=True,
        )
        self.log_label.bind(texture_size=self.log_label.setter("size"))
        self.log_label.bind(size=lambda *a: setattr(self.log_label, "text_size", (self.log_label.width, None)))

        # Log background
        with log_scroll.canvas.before:
            Color(*LOG_BG)
            self.log_bg = RoundedRectangle(pos=log_scroll.pos, size=log_scroll.size, radius=[dp(8)])
        log_scroll.bind(pos=self._update_log_bg, size=self._update_log_bg)

        log_scroll.add_widget(self.log_label)
        root.add_widget(log_scroll)

        # Timer cập nhật UI
        Clock.schedule_interval(self._update_ui, 1)

        return root

    def _update_log_bg(self, *args):
        if hasattr(self, "log_bg"):
            scroll = args[0] if args else None
            if scroll:
                self.log_bg.pos = scroll.pos
                self.log_bg.size = scroll.size

    def _add_log(self, msg):
        """Thêm log (thread-safe qua Clock)."""
        Clock.schedule_once(lambda dt: self._do_add_log(msg))

    def _do_add_log(self, msg):
        self.log_lines.append(msg)
        if len(self.log_lines) > 100:
            self.log_lines = self.log_lines[-100:]
        self.log_label.text = "\n".join(self.log_lines)

    def _update_ui(self, dt):
        if self.bot:
            s = self.bot.stats
            self.stats_label.text = f"📦 Đơn: {s['orders']}  |  🌱 Farm: {s['farmed']}  |  ❌ Lỗi: {s['errors']}"

            if self.bot.running and not self.bot.paused:
                self.status_label.text = "▶️ Đang chạy..."
                self.status_label.color = PLAY_COLOR
            elif self.bot.paused:
                self.status_label.text = "⏸️ Tạm dừng"
                self.status_label.color = PAUSE_COLOR
            else:
                self.status_label.text = "⏹️ Đã dừng"
                self.status_label.color = STOP_COLOR

    def on_play(self, *args):
        if self.bot and self.bot.paused:
            self.bot.resume()
            return

        if self.bot and self.bot.running:
            self._add_log("Bot đang chạy rồi!")
            return

        # Kết nối
        self._add_log("Đang kết nối...")
        if not self.controller.connect():
            self._add_log("❌ Không kết nối được! Cần root hoặc quyền shell")
            return

        self._add_log("✅ Đã kết nối")
        self.bot = BotEngine(self.controller, self.matcher, log_callback=self._add_log)
        self.bot.start()

    def on_pause(self, *args):
        if self.bot:
            if self.bot.paused:
                self.bot.resume()
            else:
                self.bot.pause()

    def on_restart(self, *args):
        if self.bot:
            self.bot.restart()
        else:
            self.on_play()

    def on_stop(self):
        if self.bot:
            self.bot.stop()


if __name__ == "__main__":
    AutoGameApp().run()
