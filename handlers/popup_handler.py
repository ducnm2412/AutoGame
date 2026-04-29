# ============================================================
# HANDLER POPUP - Đóng popup, dismiss reward
# ============================================================

import os
import time
from core.logger import setup_logger
from config import (
    IMAGES_BUTTONS, DELAY_ORDER, DELAY_BETWEEN_ACTIONS,
    DELAY_SCREEN_LOAD, SCREEN_WIDTH
)

logger = setup_logger()


class PopupHandler:
    """Xử lý đóng popup và reward."""

    def __init__(self, adb, matcher):
        self.adb = adb
        self.matcher = matcher

    def close_popup(self):
        """Đóng popup bằng nút X hoặc nhấn Back."""
        close_img = os.path.join(IMAGES_BUTTONS, "btn_close.png")
        if os.path.exists(close_img):
            if self.matcher.find_and_tap(self.adb, close_img):
                logger.info("  ❌ Đã đóng popup")
                time.sleep(DELAY_ORDER)
                return True

        logger.warning("  Nhấn Back để đóng")
        self.adb.press_back()
        time.sleep(DELAY_BETWEEN_ACTIONS)
        return False

    def dismiss_reward(self):
        """Đóng popup 'Chúc Mừng Nhận Được' bằng cách tap vùng trống."""
        time.sleep(DELAY_SCREEN_LOAD)
        # Tap vùng dưới cùng, tránh tap vào icon phần thưởng
        self.adb.tap(SCREEN_WIDTH // 2, 1200)
        logger.info("  🎉 Đã đóng popup phần thưởng")
        time.sleep(DELAY_ORDER)

    def tap_outside(self, x=50, y=200):
        """Tap vùng trống bên ngoài popup."""
        time.sleep(DELAY_SCREEN_LOAD)
        self.adb.tap(x, y)
        logger.info(f"  ✅ Đã tap ngoài popup tại ({x},{y})")
        time.sleep(DELAY_SCREEN_LOAD)
