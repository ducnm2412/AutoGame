# ============================================================
# HANDLER ĐƠN HÀNG - Xử lý dấu ❗ và giao hàng
# ============================================================

import os
import time
from core.logger import setup_logger
from config import (
    IMAGES_UI, IMAGES_BUTTONS,
    DELAY_ORDER, DELAY_SCREEN_LOAD,
    MAX_ORDER_RETRY
)

logger = setup_logger()


class OrderHandler:
    """Xử lý đơn hàng: tìm dấu ❗ → xử lý popup → giao hàng."""

    def __init__(self, adb, matcher, popup_handler):
        self.adb = adb
        self.matcher = matcher
        self.popup = popup_handler

    def process_orders(self):
        """
        Xử lý đơn hàng:
        1. Tìm dấu chấm than đỏ (!) → click → 'Chưa có hàng'
        2. Tìm dấu chấm than vàng (!) → click → 'Đến làm' → 'Làm' → 'Giao'
        """
        logger.info("📦 Bắt đầu XỬ LÝ ĐƠN HÀNG...")

        # Ảnh mẫu dấu chấm than
        red_templates = [
            os.path.join(IMAGES_UI, "dau_cham_than_do.png"),
            os.path.join(IMAGES_UI, "dau_cham_than.png"),
            os.path.join(IMAGES_UI, "dau_cham_than_2.png"),
        ]
        red_templates = [t for t in red_templates if os.path.exists(t)]

        yellow_template = os.path.join(IMAGES_UI, "dau_cham_than_vang.png")
        has_yellow = os.path.exists(yellow_template)

        if not red_templates and not has_yellow:
            logger.error("❌ Thiếu ảnh mẫu dấu chấm than!")
            return 0

        orders_done = 0

        for attempt in range(MAX_ORDER_RETRY):
            ss = self._screenshot()
            if ss is None:
                break

            tagged_positions = []

            # Tìm dấu đỏ
            for template in red_templates:
                found = self.matcher.find_all(ss, template, threshold=0.98)
                for x, y, conf in found:
                    tagged_positions.append((x, y, conf, "red"))

            # Tìm dấu vàng (top 5)
            if has_yellow:
                found = self.matcher.find_all(ss, yellow_template, threshold=0.98)
                found = sorted(found, key=lambda m: m[2], reverse=True)[:5]
                for x, y, conf in found:
                    tagged_positions.append((x, y, conf, "yellow"))

            tagged_positions = self._deduplicate(tagged_positions)

            if not tagged_positions:
                if attempt == 0:
                    logger.info("Không tìm thấy dấu chấm than (!) nào")
                break

            red_count = sum(1 for *_, c in tagged_positions if c == "red")
            yellow_count = sum(1 for *_, c in tagged_positions if c == "yellow")
            logger.info(
                f"Tìm thấy {len(tagged_positions)} dấu (!): "
                f"{red_count} đỏ, {yellow_count} vàng"
            )

            for x, y, conf, color in tagged_positions:
                emoji = "🔴" if color == "red" else "🟡"
                logger.info(
                    f"  {emoji} Click dấu (!) {color} tại ({x}, {y}) "
                    f"conf={conf:.2f}"
                )
                self.adb.tap(x, y)
                time.sleep(DELAY_ORDER)

                self._handle_order_popup(color)

                orders_done += 1
                logger.info(f"  ✅ Xử lý đơn #{orders_done}")
                time.sleep(DELAY_ORDER)

            time.sleep(DELAY_SCREEN_LOAD)

        logger.info(f"Đã xử lý {orders_done} đơn hàng")
        return orders_done

    # ----------------------------------------------------------
    # PRIVATE
    # ----------------------------------------------------------
    def _screenshot(self):
        """Chụp màn hình."""
        ss = self.adb.screenshot()
        if ss is None:
            logger.error("Không chụp được màn hình!")
        return ss

    def _deduplicate(self, positions, min_distance=50):
        """Loại bỏ vị trí trùng lặp, giữ confidence cao nhất."""
        if not positions:
            return []
        positions.sort(key=lambda m: m[2], reverse=True)
        filtered = []
        for pos in positions:
            x, y, conf, color = pos
            if not any(abs(x - fx) < min_distance and abs(y - fy) < min_distance
                       for fx, fy, _, _ in filtered):
                filtered.append(pos)
        return filtered

    def _handle_order_popup(self, color):
        """Xử lý popup theo màu dấu chấm than."""
        time.sleep(DELAY_SCREEN_LOAD)
        ss = self._screenshot()
        if ss is None:
            return

        if color == "red":
            btn_img = os.path.join(IMAGES_BUTTONS, "btn_chua_co_hang.png")
            if os.path.exists(btn_img):
                if self.matcher.find_and_tap(self.adb, btn_img, screenshot=ss):
                    logger.info("  ✅ Đã click 'Chưa có hàng'")
                    time.sleep(DELAY_ORDER)
                    return

        elif color == "yellow":
            btn_img = os.path.join(IMAGES_BUTTONS, "btn_den_lam.png")
            if os.path.exists(btn_img):
                if self.matcher.find_and_tap(self.adb, btn_img, screenshot=ss):
                    logger.info("  🔨 Đã click 'Đến làm'")
                    time.sleep(DELAY_SCREEN_LOAD)
                    self._click_lam_button()
                    return

        # Fallback
        self.popup.close_popup()

    def _click_lam_button(self):
        """Flow: Click 'Làm' → đóng popup → Click 'Giao'."""
        btn_lam = os.path.join(IMAGES_BUTTONS, "btn_lam.png")
        btn_lam_wide = os.path.join(IMAGES_BUTTONS, "btn_lam_wide.png")

        # Bước 1: Click nút 'Làm'
        lam_clicked = False
        for template in [btn_lam, btn_lam_wide]:
            if not os.path.exists(template):
                continue
            result = self.matcher.wait_for(self.adb, template, timeout=5, interval=0.5)
            if result:
                x, y, conf = result
                self.adb.tap(x, y)
                logger.info(f"  ✅ Đã click 'Làm' tại ({x}, {y})")
                time.sleep(DELAY_ORDER)
                lam_clicked = True
                break

        if not lam_clicked:
            logger.warning("  Không tìm thấy nút 'Làm'")
            self.popup.close_popup()
            return False

        # Bước 2: Đóng popup "Làm xong" bằng tap ngoài
        self.popup.tap_outside(50, 200)

        # Bước 3: Click nút 'Giao'
        btn_giao = os.path.join(IMAGES_BUTTONS, "btn_giao.png")
        btn_den_lam = os.path.join(IMAGES_BUTTONS, "btn_den_lam.png")

        ss = self._screenshot()
        if ss is None:
            return False

        if os.path.exists(btn_giao):
            if self.matcher.find_and_tap(self.adb, btn_giao, screenshot=ss):
                logger.info("  📦 Đã click 'Giao'")
                time.sleep(DELAY_ORDER)
                self.popup.dismiss_reward()
                return True

        if os.path.exists(btn_den_lam):
            result = self.matcher.find(ss, btn_den_lam, threshold=0.6)
            if result:
                x, y, conf = result
                self.adb.tap(x, y)
                logger.info(f"  📦 Đã click 'Giao' (vị trí den_lam) tại ({x}, {y})")
                time.sleep(DELAY_ORDER)
                self.popup.dismiss_reward()
                return True

        logger.warning("  Không tìm thấy nút 'Giao'")
        return False
