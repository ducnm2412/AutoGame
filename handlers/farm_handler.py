# ============================================================
# HANDLER TRỒNG CÂY - Nhận diện popup_menu / thu_hoach_nhanh
# ============================================================

import os
import time
from core.logger import setup_logger
from core.image_matcher import ImageMatcher
from config import FARM_PLOTS, FARM_FIRST_FLOWER, FARM_VIP_BUTTON, IMAGES_UI

DELAY_STEP = 3  # Chờ 3 giây giữa mỗi bước

logger = setup_logger()

# Đường dẫn ảnh mẫu nhận diện
THU_HOACH_NHANH_IMG = os.path.join(IMAGES_UI, "thu_hoach_nhanh.png")
POPUP_MENU_IMG = os.path.join(IMAGES_UI, "popup_menu.png")


class FarmHandler:
    """Xử lý trồng cây thông minh: nhận diện popup_menu hoặc thu_hoach_nhanh."""

    def __init__(self, adb):
        self.adb = adb
        self.matcher = ImageMatcher()

    def run(self):
        """
        Tap ô đất → chụp màn hình → nhận diện:
          1. popup_menu → chọn hoa + tưới nhanh
          2. thu_hoach_nhanh → tap thu hoạch
          3. Trường hợp khác → tap (798, 624) đóng popup
        """
        logger.info("🌱 Bắt đầu TRỒNG & THU HOẠCH...")
        total_harvested = 0
        total_planted = 0

        for idx, (px, py) in enumerate(FARM_PLOTS):
            logger.info(f"  --- Ô đất #{idx + 1} tại ({px}, {py}) ---")

            while True:
                self.adb.tap(px, py)
                logger.info(f"  Tap ô đất ({px}, {py})")
                time.sleep(DELAY_STEP)

                # Chụp màn hình và nhận diện
                screenshot = self.adb.screenshot()
                if screenshot is None:
                    logger.warning("  Không chụp được màn hình!")
                    break

                has_harvest = self.matcher.find(screenshot, THU_HOACH_NHANH_IMG)
                has_menu = self.matcher.find(screenshot, POPUP_MENU_IMG)

                if has_harvest:
                    # === THU HOẠCH NHANH ===
                    hx, hy, conf = has_harvest
                    self.adb.tap(hx, hy)
                    logger.info(f"  ⚡ Thu hoạch nhanh tại ({hx}, {hy}) conf={conf:.3f}")
                    total_harvested += 1
                    time.sleep(DELAY_STEP)
                    # Lặp lại tap ô đất

                elif has_menu:
                    # === POPUP MENU → Chọn hoa + Tưới nhanh ===
                    fx, fy = FARM_FIRST_FLOWER
                    self.adb.tap(fx, fy)
                    logger.info(f"  🌸 Chọn hoa tại ({fx}, {fy})")
                    time.sleep(DELAY_STEP)

                    # Tưới nhanh
                    self.adb.tap(px, py)
                    logger.info(f"  Tap ô đất ({px}, {py})")
                    time.sleep(DELAY_STEP)
                    vx, vy = FARM_VIP_BUTTON
                    self.adb.tap(vx, vy)
                    logger.info(f"  ⚡ Tưới nhanh tại ({vx}, {vy})")
                    time.sleep(DELAY_STEP)

                    total_planted += 1
                    # Lặp lại tap ô đất (sẽ thấy thu_hoach_nhanh)

                else:
                    # === TRƯỜNG HỢP KHÁC → Đóng popup ===
                    self.adb.tap(798, 624)
                    logger.info(f"  ⏭️ Đóng popup (798, 624)")
                    time.sleep(DELAY_STEP)
                    break

            logger.info(f"  ✅ Xong ô #{idx + 1}")

        logger.info(f"🌾 Kết quả: thu hoạch {total_harvested}, trồng mới {total_planted}")
        return total_harvested + total_planted
