# ============================================================
# TEST NHẬN DIỆN THU HOẠCH NHANH
# Chụp màn hình → detect thu_hoach_nhanh giống detect dấu chấm than
# ============================================================

import os
from core.adb_controller import ADBController
from core.image_matcher import ImageMatcher
from core.logger import setup_logger
from config import SCREENSHOTS_DIR, IMAGES_UI

logger = setup_logger()


def main():
    adb = ADBController()
    if not adb.connect():
        logger.error("Không kết nối được!")
        return

    matcher = ImageMatcher()

    # Chụp màn hình hiện tại
    screen_path = os.path.join(SCREENSHOTS_DIR, "detect_screen.png")
    screenshot = adb.screenshot(save_path=screen_path)
    if screenshot is None:
        logger.error("Không chụp được màn hình!")
        adb.disconnect()
        return

    logger.info(f"Screenshot: {screenshot.mode} {screenshot.size}")

    # --- Nhận diện dấu chấm than đỏ ---
    red_path = os.path.join(IMAGES_UI, "dau_cham_than_do.png")
    red_result = matcher.find(screenshot, red_path)
    red_all = matcher.find_all(screenshot, red_path)
    logger.info(f"Red:    {red_result}")
    logger.info(f"Red all({len(red_all)}): {red_all[:5]}")

    # --- Nhận diện dấu chấm than vàng ---
    yellow_path = os.path.join(IMAGES_UI, "dau_cham_than_vang.png")
    yellow_result = matcher.find(screenshot, yellow_path)
    yellow_all = matcher.find_all(screenshot, yellow_path)
    logger.info(f"Yellow:    {yellow_result}")
    logger.info(f"Yellow all({len(yellow_all)}): {yellow_all[:5]}")

    # --- Nhận diện Thu hoạch nhanh ---
    thu_hoach_path = os.path.join(IMAGES_UI, "thu_hoach_nhanh.png")
    if not os.path.exists(thu_hoach_path):
        logger.error(f"Không tìm thấy ảnh mẫu: {thu_hoach_path}")
    else:
        thu_hoach_result = matcher.find(screenshot, thu_hoach_path)
        thu_hoach_all = matcher.find_all(screenshot, thu_hoach_path)
        logger.info(f"Thu hoạch nhanh:    {thu_hoach_result}")
        logger.info(f"Thu hoạch nhanh all({len(thu_hoach_all)}): {thu_hoach_all[:5]}")

    # Lưu kết quả ra file
    result_path = os.path.join(SCREENSHOTS_DIR, "detect_result.txt")
    with open(result_path, "w", encoding="utf-8") as f:
        f.write(f"Screenshot: {screenshot.mode} {screenshot.size}\n")
        f.write(f"Red:    {red_result}\n")
        f.write(f"Red all({len(red_all)}): {red_all[:5]}\n")
        f.write(f"Yellow:    {yellow_result}\n")
        f.write(f"Yellow all({len(yellow_all)}): {yellow_all[:5]}\n")
        if os.path.exists(thu_hoach_path):
            f.write(f"Thu hoạch nhanh:    {thu_hoach_result}\n")
            f.write(f"Thu hoạch nhanh all({len(thu_hoach_all)}): {thu_hoach_all[:5]}\n")

    logger.info(f"Đã lưu kết quả: {result_path}")
    adb.disconnect()
    logger.info("DONE")


if __name__ == "__main__":
    main()
