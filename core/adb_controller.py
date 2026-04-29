# ============================================================
# MODULE ĐIỀU KHIỂN ADB - KẾT NỐI VÀ TƯƠNG TÁC VỚI LDPLAYER
# ============================================================

import subprocess
import time
import os
import io
from PIL import Image
from core.logger import setup_logger
from config import (
    ADB_HOST, ADB_PORT, SCREENSHOTS_DIR,
    SCREEN_WIDTH, SCREEN_HEIGHT, DELAY_TAP
)

logger = setup_logger()


class ADBController:
    """Điều khiển thiết bị Android qua ADB."""

    def __init__(self, host=ADB_HOST, port=ADB_PORT):
        self.device_address = f"{host}:{port}"
        self.connected = False
        self._adb_path = self._find_adb()

    def _find_adb(self):
        """Tìm đường dẫn ADB."""
        try:
            result = subprocess.run(
                ["adb", "version"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                logger.info("Tìm thấy ADB trong PATH")
                return "adb"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        ldplayer_paths = [
            r"C:\LDPlayer\LDPlayer9\adb.exe",
            r"C:\LDPlayer\LDPlayer4.0\adb.exe",
            r"C:\Program Files\LDPlayer\LDPlayer9\adb.exe",
            r"C:\Program Files (x86)\LDPlayer\LDPlayer9\adb.exe",
            r"C:\LDPlayer9\adb.exe",
        ]
        for path in ldplayer_paths:
            if os.path.exists(path):
                logger.info(f"Tìm thấy ADB tại: {path}")
                return path

        logger.warning("Không tìm thấy ADB! Sử dụng 'adb' mặc định")
        return "adb"

    def _run_adb(self, *args, timeout=10):
        """Chạy lệnh ADB và trả về output."""
        cmd = [self._adb_path, "-s", self.device_address] + list(args)
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            return result.stdout.strip(), result.returncode
        except subprocess.TimeoutExpired:
            logger.error(f"ADB timeout: {' '.join(cmd)}")
            return "", 1
        except Exception as e:
            logger.error(f"ADB error: {e}")
            return "", 1

    def _run_adb_bytes(self, *args, timeout=10):
        """Chạy lệnh ADB và trả về output dạng bytes."""
        cmd = [self._adb_path, "-s", self.device_address] + list(args)
        try:
            result = subprocess.run(
                cmd, capture_output=True, timeout=timeout
            )
            return result.stdout, result.returncode
        except subprocess.TimeoutExpired:
            logger.error(f"ADB timeout: {' '.join(cmd)}")
            return b"", 1
        except Exception as e:
            logger.error(f"ADB error: {e}")
            return b"", 1

    def connect(self):
        """Kết nối tới LDPlayer qua ADB."""
        logger.info(f"Đang kết nối tới {self.device_address}...")

        subprocess.run(
            [self._adb_path, "start-server"],
            capture_output=True, timeout=10
        )
        time.sleep(2)

        output, code = self._run_adb("connect", self.device_address)
        if "connected" in output.lower() and "offline" not in output.lower():
            self.connected = True
            logger.info(f"✅ Đã kết nối: {self.device_address}")
            return True

        logger.info("Thử lại kết nối sau 3s...")
        time.sleep(3)
        output, code = self._run_adb("connect", self.device_address)
        if "connected" in output.lower():
            if self.is_device_ready():
                self.connected = True
                logger.info(f"✅ Đã kết nối: {self.device_address}")
                return True

        logger.info("Thử kết nối emulator-5554...")
        self.device_address = "emulator-5554"
        if self.is_device_ready():
            self.connected = True
            logger.info(f"✅ Đã kết nối qua: {self.device_address}")
            return True

        self.device_address = f"{ADB_HOST}:{ADB_PORT}"
        logger.error(f"❌ Không thể kết nối: {output}")
        return False

    def disconnect(self):
        """Ngắt kết nối ADB."""
        self._run_adb("disconnect", self.device_address)
        self.connected = False
        logger.info("Đã ngắt kết nối ADB")

    def tap(self, x, y):
        """Tap vào tọa độ (x, y) trên màn hình."""
        self._run_adb("shell", "input", "tap", str(int(x)), str(int(y)))
        logger.debug(f"Tap: ({x}, {y})")
        time.sleep(DELAY_TAP)

    def long_press(self, x, y, duration_ms=1000):
        """Nhấn giữ tại tọa độ (x, y)."""
        self._run_adb(
            "shell", "input", "swipe",
            str(int(x)), str(int(y)),
            str(int(x)), str(int(y)),
            str(duration_ms)
        )
        logger.debug(f"Long press: ({x}, {y}) - {duration_ms}ms")
        time.sleep(DELAY_TAP)

    def swipe(self, x1, y1, x2, y2, duration_ms=500):
        """Vuốt từ (x1,y1) đến (x2,y2)."""
        self._run_adb(
            "shell", "input", "swipe",
            str(int(x1)), str(int(y1)),
            str(int(x2)), str(int(y2)),
            str(duration_ms)
        )
        logger.debug(f"Swipe: ({x1},{y1}) -> ({x2},{y2})")
        time.sleep(DELAY_TAP)

    def screenshot(self, save_path=None):
        """Chụp màn hình và trả về PIL Image."""
        image = self._screenshot_pull(save_path)
        if image:
            return image
        image = self._screenshot_pipe(save_path)
        if image:
            return image
        logger.error("Không thể chụp màn hình bằng cả 2 phương pháp!")
        return None

    def _screenshot_pull(self, save_path=None):
        """Chụp màn hình bằng cách pull file."""
        remote_path = "/sdcard/autogame_screen.png"
        local_path = save_path or os.path.join(SCREENSHOTS_DIR, "temp_screen.png")
        _, code1 = self._run_adb("shell", "screencap", "-p", remote_path, timeout=15)
        if code1 != 0:
            return None
        _, code2 = self._run_adb("pull", remote_path, local_path, timeout=15)
        if code2 != 0:
            return None
        self._run_adb("shell", "rm", remote_path)
        try:
            image = Image.open(local_path)
            logger.debug(f"Screenshot OK: {image.size}")
            return image
        except Exception as e:
            logger.error(f"Lỗi đọc screenshot file: {e}")
            return None

    def _screenshot_pipe(self, save_path=None):
        """Chụp màn hình qua pipe."""
        raw_data, code = self._run_adb_bytes("shell", "screencap", "-p", timeout=15)
        if code != 0 or len(raw_data) < 100:
            return None
        raw_data = raw_data.replace(b"\r\n", b"\n")
        try:
            image = Image.open(io.BytesIO(raw_data))
            if save_path:
                image.save(save_path)
            return image
        except Exception:
            return None

    def get_screen_size(self):
        """Lấy kích thước màn hình."""
        output, _ = self._run_adb("shell", "wm", "size")
        if "x" in output:
            parts = output.split(":")[-1].strip().split("x")
            return int(parts[0]), int(parts[1])
        return SCREEN_WIDTH, SCREEN_HEIGHT

    def is_device_ready(self):
        """Kiểm tra thiết bị có sẵn sàng không."""
        output, code = self._run_adb("shell", "echo", "ok")
        return output.strip() == "ok"

    def key_event(self, keycode):
        """Gửi key event."""
        self._run_adb("shell", "input", "keyevent", str(keycode))
        logger.debug(f"Key event: {keycode}")

    def press_back(self):
        """Nhấn nút Back."""
        self.key_event(4)

    def press_home(self):
        """Nhấn nút Home."""
        self.key_event(3)
