# ============================================================
# CÔNG CỤ CHỤP ẢNH MẪU - CAPTURE REFERENCE IMAGES
# ============================================================
# Chạy tool này để chụp ảnh mẫu từ game.
# Sử dụng: python capture_tool.py
# ============================================================

import os
import sys
import time
from adb_controller import ADBController
from config import (
    IMAGES_CROPS, IMAGES_BUTTONS, IMAGES_ORDERS, IMAGES_UI,
    SCREENSHOTS_DIR
)


def main():
    adb = ADBController()
    if not adb.connect():
        print("❌ Không kết nối được LDPlayer!")
        return

    print("=" * 50)
    print("🖼️  CÔNG CỤ CHỤP ẢNH MẪU")
    print("=" * 50)

    while True:
        print("\nChọn chức năng:")
        print("1. Chụp toàn màn hình")
        print("2. Chụp vùng cắt (crop region)")
        print("3. Xem tọa độ khi click")
        print("0. Thoát")

        choice = input("\n> ").strip()

        if choice == "0":
            break
        elif choice == "1":
            capture_fullscreen(adb)
        elif choice == "2":
            capture_region(adb)
        elif choice == "3":
            coordinate_finder(adb)


def capture_fullscreen(adb):
    """Chụp toàn màn hình."""
    print("\nChọn thư mục lưu:")
    print("1. crops (cây trồng)")
    print("2. buttons (nút bấm)")
    print("3. orders (đơn hàng)")
    print("4. ui (giao diện)")
    print("5. screenshots (chung)")

    dirs = {
        "1": IMAGES_CROPS,
        "2": IMAGES_BUTTONS,
        "3": IMAGES_ORDERS,
        "4": IMAGES_UI,
        "5": SCREENSHOTS_DIR,
    }

    d = input("> ").strip()
    save_dir = dirs.get(d, SCREENSHOTS_DIR)

    name = input("Tên file (không cần .png): ").strip()
    if not name:
        name = f"screen_{int(time.time())}"

    path = os.path.join(save_dir, f"{name}.png")
    img = adb.screenshot(save_path=path)
    if img:
        print(f"✅ Đã lưu: {path}")
        print(f"   Kích thước: {img.size}")
    else:
        print("❌ Không chụp được!")


def capture_region(adb):
    """Chụp và cắt vùng ảnh."""
    print("\nChụp màn hình trước...")
    img = adb.screenshot()
    if img is None:
        print("❌ Không chụp được!")
        return

    # Lưu full screen tạm
    temp_path = os.path.join(SCREENSHOTS_DIR, "temp_full.png")
    img.save(temp_path)
    print(f"Đã chụp full screen: {temp_path}")
    print(f"Kích thước: {img.size}")

    print("\nNhập tọa độ vùng cần cắt:")
    try:
        x1 = int(input("  x1 (trái): "))
        y1 = int(input("  y1 (trên): "))
        x2 = int(input("  x2 (phải): "))
        y2 = int(input("  y2 (dưới): "))
    except ValueError:
        print("❌ Tọa độ không hợp lệ!")
        return

    cropped = img.crop((x1, y1, x2, y2))

    print("\nChọn thư mục lưu:")
    print("1. crops  2. buttons  3. orders  4. ui")
    dirs = {"1": IMAGES_CROPS, "2": IMAGES_BUTTONS, "3": IMAGES_ORDERS, "4": IMAGES_UI}
    d = input("> ").strip()
    save_dir = dirs.get(d, IMAGES_UI)

    name = input("Tên file: ").strip()
    if not name:
        name = f"crop_{int(time.time())}"

    path = os.path.join(save_dir, f"{name}.png")
    cropped.save(path)
    print(f"✅ Đã lưu: {path}")
    print(f"   Vùng: ({x1},{y1}) -> ({x2},{y2})")
    print(f"   Kích thước: {cropped.size}")


def coordinate_finder(adb):
    """Chụp màn hình liên tục để xem tọa độ."""
    print("\n📍 CHẾ ĐỘ XEM TỌA ĐỘ")
    print("Mở ảnh screenshot và ghi nhận tọa độ x,y.")
    print("Nhấn Enter để chụp lại, 'q' để thoát.\n")

    count = 0
    while True:
        count += 1
        path = os.path.join(SCREENSHOTS_DIR, f"coord_{count}.png")
        img = adb.screenshot(save_path=path)
        if img:
            print(f"[{count}] Đã chụp: {path} ({img.size})")
            print("    Mở file ảnh bằng Paint/Photoshop để xem tọa độ pixel")

        cmd = input("Enter=chụp tiếp, q=thoát > ").strip().lower()
        if cmd == "q":
            break


if __name__ == "__main__":
    main()
