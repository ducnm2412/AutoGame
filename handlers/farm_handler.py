# ============================================================
# HANDLER NÔNG TRẠI - Thu hoạch & Trồng cây
# ============================================================

import os
import time
from core.logger import setup_logger
from config import (
    FARM_PLOTS, CROPS,
    IMAGES_CROPS, IMAGES_BUTTONS, IMAGES_ORDERS, IMAGES_UI,
    DELAY_HARVEST, DELAY_PLANT
)

logger = setup_logger()


class FarmHandler:
    """Xử lý thu hoạch và trồng cây."""

    def __init__(self, adb, matcher):
        self.adb = adb
        self.matcher = matcher

    # ----------------------------------------------------------
    # THU HOẠCH
    # ----------------------------------------------------------
    def harvest(self):
        """
        Thu hoạch bằng cách tap vào 1 ô trong vườn.
        Sau khi tap, popup hiện 'Thu hoạch' / 'Thu hoạch nhanh'.
        Click vào nút thu hoạch nhanh (hoặc thu hoạch thường).
        """
        logger.info("🌾 Bắt đầu THU HOẠCH...")

        # Bước 1: Tap vào vườn
        farm_x, farm_y = FARM_PLOTS[0] if FARM_PLOTS else (200, 850)
        self.adb.tap(farm_x, farm_y)
        logger.info(f"  Tap vườn tại ({farm_x}, {farm_y})")
        time.sleep(DELAY_HARVEST + 0.5)

        # Bước 2: Tìm nút "Thu hoạch" → tap sang phải để click "Thu hoạch nhanh"
        btn_thuong = os.path.join(IMAGES_BUTTONS, "btn_thu_hoach.png")

        ss = self._screenshot()
        if ss is None:
            return 0

        if os.path.exists(btn_thuong):
            result = self.matcher.find(ss, btn_thuong)
            if result:
                x, y, conf = result
                # Nút "Thu hoạch nhanh" nằm bên phải nút "Thu hoạch" (~+160px)
                vip_x = x + 160
                self.adb.tap(vip_x, y)
                logger.info(f"  🌾 Đã click 'Thu hoạch nhanh' tại ({vip_x}, {y})")
                time.sleep(DELAY_HARVEST)
                return 1

        logger.info("  Không thấy nút thu hoạch (chưa chín hoặc đã thu)")
        # Tap ngoài để đóng popup nếu có
        self.adb.tap(700, 400)
        time.sleep(0.3)
        return 0

    # ----------------------------------------------------------
    # TRỒNG CÂY
    # ----------------------------------------------------------
    def plant(self):
        """Trồng cây tại các ô trống."""
        logger.info("🌱 Bắt đầu TRỒNG CÂY...")

        # Tap vào ô đất trống để mở menu trồng
        farm_x, farm_y = FARM_PLOTS[0] if FARM_PLOTS else (180, 670)
        self.adb.tap(farm_x, farm_y)
        logger.info(f"  Tap ô đất tại ({farm_x}, {farm_y})")
        time.sleep(1.5)

        # Chụp màn hình kiểm tra menu đã mở chưa
        ss = self._screenshot()
        if ss is None:
            return 0

        # Click vào hoa đầu tiên trong menu (vị trí cố định: góc trái trên của lưới hoa)
        first_flower_x, first_flower_y = 90, 1050
        self.adb.tap(first_flower_x, first_flower_y)
        logger.info(f"  🌸 Đã chọn hoa đầu tiên tại ({first_flower_x}, {first_flower_y})")
        time.sleep(DELAY_PLANT)

        return 1

    # ----------------------------------------------------------
    # PRIVATE
    # ----------------------------------------------------------
    def _screenshot(self):
        ss = self.adb.screenshot()
        if ss is None:
            logger.error("Không chụp được màn hình!")
        return ss

    def _find_empty_plots(self, screenshot):
        """Tìm các ô trống trên màn hình."""
        empty_img = os.path.join(IMAGES_UI, "o_trong.png")
        if os.path.exists(empty_img):
            plots = self.matcher.find_all(screenshot, empty_img)
            logger.info(f"Tìm thấy {len(plots)} ô trống")
            return plots
        else:
            logger.info("Dùng vị trí ô cố định để trồng")
            return [(x, y, 1.0) for x, y in FARM_PLOTS]

    def _get_needed_crops(self):
        """Xác định cây cần trồng dựa trên đơn hàng."""
        needed = []
        ss = self._screenshot()
        if ss is None:
            return list(CROPS.keys())[:1]

        for crop_name, crop_info in CROPS.items():
            order_img = os.path.join(IMAGES_ORDERS, f"order_{crop_name}.png")
            if os.path.exists(order_img):
                if self.matcher.exists(ss, order_img):
                    needed.append(crop_name)
                    logger.debug(f"Đơn hàng cần: {crop_name}")

        if not needed:
            sorted_crops = sorted(
                CROPS.items(), key=lambda x: x[1]["priority"]
            )
            needed = [name for name, _ in sorted_crops[:3]]
            logger.info(f"Trồng mặc định theo ưu tiên: {needed}")

        return needed

    def _select_crop(self, crop_name):
        """Chọn loại cây để trồng từ menu."""
        crop_info = CROPS.get(crop_name)
        if not crop_info:
            logger.warning(f"Không tìm thấy config cây: {crop_name}")
            return False

        crop_img = os.path.join(IMAGES_CROPS, crop_info["image"])
        if os.path.exists(crop_img):
            return self.matcher.find_and_tap(self.adb, crop_img)
        else:
            logger.warning(f"Thiếu ảnh mẫu: {crop_img}")
            return False

    def has_harvest_template(self):
        """Thu hoạch luôn sẵn sàng (tap vị trí cố định)."""
        return True

    def has_crop_templates(self):
        """Kiểm tra có ảnh mẫu cây trồng không."""
        return any(
            os.path.exists(os.path.join(IMAGES_CROPS, info["image"]))
            for info in CROPS.values()
        )
