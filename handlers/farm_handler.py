# ============================================================
# HANDLER TRỒNG CÂY - Trồng → Tưới nhanh → Thu hoạch nhanh
# ============================================================

import time
from core.logger import setup_logger
from config import FARM_PLOTS, FARM_FIRST_FLOWER, FARM_VIP_BUTTON

DELAY_STEP = 3  # Chờ 3 giây giữa mỗi bước

logger = setup_logger()


class FarmHandler:
    """Xử lý trồng cây: Tap ô đất → Chọn hoa → Tưới nhanh → Thu hoạch nhanh."""

    def __init__(self, adb):
        self.adb = adb

    def run(self):
        """
        Chạy toàn bộ flow trồng cây cho tất cả ô đất:
        1. Tap ô đất → menu trồng → chọn hoa đầu tiên
        2. Tap ô đất → menu tưới → Tưới nhanh (VIP)
        3. Tap ô đất → menu thu hoạch → Thu hoạch nhanh (VIP)
        """
        logger.info("🌱 Bắt đầu TRỒNG CÂY...")
        total = 0

        for idx, (px, py) in enumerate(FARM_PLOTS):
            logger.info(f"  --- Ô đất #{idx + 1} tại ({px}, {py}) ---")

            # Bước 1: Trồng cây
            if not self._plant(px, py):
                logger.warning(f"  ❌ Không trồng được ô #{idx + 1}")
                continue

            # Bước 2: Tưới nhanh
            if not self._vip_action(px, py, "Tưới nhanh"):
                logger.warning(f"  ❌ Không tưới được ô #{idx + 1}")
                continue

            # Bước 3: Thu hoạch nhanh
            if not self._vip_action(px, py, "Thu hoạch nhanh"):
                logger.warning(f"  ❌ Không thu hoạch được ô #{idx + 1}")
                continue

            # Bước 4: Tap (817, 1185) để xác nhận
            self.adb.tap(817, 1185)
            logger.info(f"  ✅ Tap (817, 1185)")
            time.sleep(DELAY_STEP)

            total += 1
            logger.info(f"  ✅ Hoàn thành ô #{idx + 1}")

        logger.info(f"🌾 Đã trồng & thu hoạch {total}/{len(FARM_PLOTS)} ô")
        return total

    # ----------------------------------------------------------
    # PRIVATE
    # ----------------------------------------------------------
    def _plant(self, plot_x, plot_y):
        """Tap ô đất → chọn hoa đầu tiên."""
        fx, fy = FARM_FIRST_FLOWER

        self.adb.tap(plot_x, plot_y)
        logger.info(f"  Tap ô đất ({plot_x}, {plot_y})")
        time.sleep(DELAY_STEP)

        self.adb.tap(fx, fy)
        logger.info(f"  🌸 Chọn hoa tại ({fx}, {fy})")
        time.sleep(DELAY_STEP)

        return True

    def _vip_action(self, plot_x, plot_y, action_name):
        """Tap ô đất → Tap nút VIP (Tưới nhanh / Thu hoạch nhanh)."""
        vx, vy = FARM_VIP_BUTTON

        self.adb.tap(plot_x, plot_y)
        logger.info(f"  Tap ô đất ({plot_x}, {plot_y})")
        time.sleep(DELAY_STEP)

        self.adb.tap(vx, vy)
        logger.info(f"  ⚡ {action_name} tại ({vx}, {vy})")
        time.sleep(DELAY_STEP)

        return True
