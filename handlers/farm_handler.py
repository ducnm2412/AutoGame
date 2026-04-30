# ============================================================
# HANDLER NÔNG TRẠI - Thu hoạch & Trồng cây
# ============================================================
#
# Flow trồng cây:
#   1. Chụp màn hình → tìm ô trống (o_trong.png)
#   2. Tap vào ô trống → mở menu chọn hoa
#   3. Bật "Trồng nhanh" (checkbox) → trồng tất cả ô cùng lúc
#   4. Chọn hoa đầu tiên trong danh sách
#   5. Tất cả ô trống được trồng cùng 1 loại hoa
#
# Flow thu hoạch:
#   1. Tap vào vườn (vị trí cố định)
#   2. Tìm nút "Thu hoạch" trên popup
#   3. Click offset sang phải → "Thu hoạch nhanh" (VIP)
# ============================================================

import os
import time
from core.logger import setup_logger
from config import (
    FARM_PLOTS, CROPS,
    IMAGES_CROPS, IMAGES_BUTTONS, IMAGES_ORDERS, IMAGES_UI,
    DELAY_HARVEST, DELAY_PLANT,
    PLANT_MENU,
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
        Thu hoạch bằng cách tap vào ô trong vườn.
        Sau khi tap, tìm nút 'Thu hoạch nhanh' (VIP) → click.
        """
        logger.info("🌾 Bắt đầu THU HOẠCH...")

        # Bước 1: Tap vào vườn
        farm_x, farm_y = FARM_PLOTS[0] if FARM_PLOTS else (180, 670)
        self.adb.tap(farm_x, farm_y)
        logger.info(f"  Tap vườn tại ({farm_x}, {farm_y})")
        time.sleep(1.5)

        # Bước 2: Tìm nút "Thu hoạch nhanh" (VIP)
        btn_nhanh = os.path.join(IMAGES_BUTTONS, "btn_thu_hoach_nhanh.png")
        ss = self._screenshot()
        if ss is None:
            return 0

        if os.path.exists(btn_nhanh):
            result = self.matcher.find(ss, btn_nhanh)
            if result:
                x, y, conf = result
                self.adb.tap(x, y)
                logger.info(f"  🌾 Đã click 'Thu hoạch nhanh' tại ({x}, {y})")
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
        """
        Trồng hoa và tưới nhanh.

        Flow:
        1. Tap vào ô đất cố định → mở menu chọn hoa
        2. Chọn hoa đầu tiên trong lưới
        3. Tap lại ô đất → mở menu tưới
        4. Tìm nút "Tưới nhanh" (VIP) → tap để tưới tất cả
        """
        logger.info("🌱 Bắt đầu TRỒNG CÂY...")

        # ---- Bước 1: Tap vào ô đất cố định → mở menu chọn hoa ----
        plot_x, plot_y = FARM_PLOTS[0] if FARM_PLOTS else (180, 670)
        self.adb.tap(plot_x, plot_y)
        logger.info(f"  Tap ô đất tại ({plot_x}, {plot_y})")
        time.sleep(2.0)  # Chờ menu mở

        # ---- Bước 2: Chọn hoa đầu tiên trong lưới ----
        flower_x, flower_y = PLANT_MENU["first_flower"]
        self.adb.tap(flower_x, flower_y)
        logger.info(f"  🌸 Chọn hoa tại ({flower_x}, {flower_y})")
        time.sleep(DELAY_PLANT + 1.0)

        logger.info("  ✅ Đã trồng cây")

        # ---- Bước 3: Tap lại ô đất → mở menu tưới ----
        self.adb.tap(plot_x, plot_y)
        logger.info(f"  Tap lại ô đất tại ({plot_x}, {plot_y})")
        time.sleep(1.5)

        # ---- Bước 4: Tìm và click "Tưới nhanh" (VIP) ----
        btn_tuoi_nhanh = os.path.join(IMAGES_BUTTONS, "btn_tuoi_nhanh.png")
        if os.path.exists(btn_tuoi_nhanh):
            ss = self._screenshot()
            if ss is not None:
                result = self.matcher.find(ss, btn_tuoi_nhanh)
                if result:
                    x, y, conf = result
                    self.adb.tap(x, y)
                    logger.info(f"  💧 Đã click 'Tưới nhanh' tại ({x}, {y})")
                    time.sleep(1.0)
                    return 1
                else:
                    logger.info("  Không thấy nút 'Tưới nhanh' (có thể đã tưới)")
        else:
            logger.warning("  Thiếu ảnh mẫu btn_tuoi_nhanh.png")

        return 1

    def _plant_single_fallback(self, empty_plots):
        """
        Fallback: trồng từng ô một nếu "Trồng nhanh" không hoạt động.

        Với mỗi ô trống:
        1. Tap ô trống → mở menu
        2. Chọn hoa đầu tiên (không bật Trồng nhanh)
        3. Lặp lại cho ô tiếp theo
        """
        planted = 0

        # Tap ngoài để đóng menu cũ (nếu còn mở)
        self.adb.tap(450, 300)
        time.sleep(1.0)

        for i, (px, py, _) in enumerate(empty_plots[:6]):
            # Giới hạn 6 ô để tránh timeout
            logger.info(f"  Trồng ô {i+1}/{min(len(empty_plots), 6)}...")

            self.adb.tap(int(px), int(py))
            time.sleep(2.0)

            # Chọn hoa đầu tiên
            flower_x, flower_y = PLANT_MENU["first_flower"]
            self.adb.tap(flower_x, flower_y)
            time.sleep(DELAY_PLANT + 0.5)

            planted += 1

        logger.info(f"  ✅ Trồng từng ô xong: {planted} ô")
        return planted

    # ----------------------------------------------------------
    # KIỂM TRA SẴN SÀNG
    # ----------------------------------------------------------
    def has_harvest_template(self):
        """Thu hoạch luôn sẵn sàng (tap vị trí cố định)."""
        return True

    def has_crop_templates(self):
        """
        Kiểm tra có thể trồng cây không.

        Trả về True nếu:
        - Có ảnh mẫu ô trống (o_trong.png) để nhận diện, HOẶC
        - Có vị trí ô cố định (FARM_PLOTS) để fallback
        """
        # Ưu tiên: có ảnh mẫu ô trống
        o_trong = os.path.join(IMAGES_UI, "o_trong.png")
        if os.path.exists(o_trong):
            return True

        # Fallback: có vị trí cố định
        if FARM_PLOTS:
            return True

        return False

    # ----------------------------------------------------------
    # PRIVATE HELPERS
    # ----------------------------------------------------------
    def _screenshot(self):
        """Chụp màn hình, trả về PIL Image hoặc None."""
        ss = self.adb.screenshot()
        if ss is None:
            logger.error("Không chụp được màn hình!")
        return ss

    def _find_empty_plots(self, screenshot):
        """
        Tìm các ô trống trên màn hình.

        Cách hoạt động:
        - Dùng ảnh mẫu o_trong.png (ô đất trống màu nâu)
        - OpenCV template matching tìm TẤT CẢ vị trí khớp
        - Trả về list[(x, y, confidence)]

        Fallback: nếu không có ảnh mẫu → dùng vị trí cố định FARM_PLOTS
        """
        empty_img = os.path.join(IMAGES_UI, "o_trong.png")
        if os.path.exists(empty_img):
            plots = self.matcher.find_all(screenshot, empty_img)
            logger.info(f"  Tìm thấy {len(plots)} ô trống (image matching)")
            return plots
        else:
            logger.info("  Dùng vị trí ô cố định FARM_PLOTS")
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
