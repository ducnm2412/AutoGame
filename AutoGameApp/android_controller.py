# ============================================================
# ANDROID CONTROLLER - Thay thế ADB bằng shell commands
# Chạy trực tiếp trên Android (cần root hoặc quyền shell)
# ============================================================

import os
import subprocess
import time
from PIL import Image

DELAY_TAP = 0.3
SCREEN_PATH = "/sdcard/autogame_screen.png"


class AndroidController:
    """Điều khiển Android bằng shell commands (thay ADB)."""

    def __init__(self):
        self.connected = False

    def connect(self):
        """Kiểm tra quyền shell."""
        try:
            result = subprocess.run(
                ["su", "-c", "echo ok"],
                capture_output=True, text=True, timeout=5
            )
            if "ok" in result.stdout:
                self.connected = True
                return True
        except Exception:
            pass

        # Thử không root
        try:
            result = subprocess.run(
                ["sh", "-c", "echo ok"],
                capture_output=True, text=True, timeout=5
            )
            if "ok" in result.stdout:
                self.connected = True
                return True
        except Exception:
            pass

        return False

    def disconnect(self):
        self.connected = False

    def tap(self, x, y):
        """Tap vào tọa độ (x, y)."""
        try:
            subprocess.run(
                ["sh", "-c", f"input tap {int(x)} {int(y)}"],
                capture_output=True, timeout=5
            )
        except Exception:
            pass
        time.sleep(DELAY_TAP)

    def screenshot(self, save_path=None):
        """Chụp màn hình, trả về PIL Image."""
        local_path = save_path or SCREEN_PATH
        try:
            subprocess.run(
                ["sh", "-c", f"screencap -p {local_path}"],
                capture_output=True, timeout=15
            )
            if os.path.exists(local_path):
                image = Image.open(local_path)
                return image
        except Exception:
            pass
        return None

    def get_screen_size(self):
        """Lấy kích thước màn hình."""
        try:
            result = subprocess.run(
                ["sh", "-c", "wm size"],
                capture_output=True, text=True, timeout=5
            )
            if "x" in result.stdout:
                parts = result.stdout.split(":")[-1].strip().split("x")
                return int(parts[0]), int(parts[1])
        except Exception:
            pass
        return 900, 1600

    def is_device_ready(self):
        return self.connected
