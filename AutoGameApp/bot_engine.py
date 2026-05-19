# ============================================================
# BOT ENGINE - Logic bot cho Android APK
# ============================================================

import os
import time
import threading

# Tọa độ cố định (900x1600)
FARM_PLOTS = [(533, 1396)]
FARM_FIRST_FLOWER = (90, 960)
FARM_VIP_BUTTON = (628, 1179)
DELAY_STEP = 3

# Đường dẫn ảnh mẫu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_UI = os.path.join(BASE_DIR, "images", "ui")
IMAGES_BUTTONS = os.path.join(BASE_DIR, "images", "buttons")

THU_HOACH_NHANH_IMG = os.path.join(IMAGES_UI, "thu_hoach_nhanh.png")
POPUP_MENU_IMG = os.path.join(IMAGES_UI, "popup_menu.png")
DAU_CHAM_THAN_DO_IMG = os.path.join(IMAGES_UI, "dau_cham_than_do.png")
DAU_CHAM_THAN_VANG_IMG = os.path.join(IMAGES_UI, "dau_cham_than_vang.png")

BTN_DEN_LAM = os.path.join(IMAGES_BUTTONS, "btn_den_lam.png")
BTN_LAM = os.path.join(IMAGES_BUTTONS, "btn_lam.png")
BTN_GIAO = os.path.join(IMAGES_BUTTONS, "btn_giao.png")
BTN_CHUA_CO_HANG = os.path.join(IMAGES_BUTTONS, "btn_chua_co_hang.png")
BTN_CLOSE = os.path.join(IMAGES_BUTTONS, "btn_close.png")


class BotEngine:
    """Bot engine chạy trên Android."""

    def __init__(self, controller, matcher, log_callback=None):
        self.ctrl = controller
        self.matcher = matcher
        self.log = log_callback or print
        self.running = False
        self.paused = False
        self._thread = None
        self.stats = {"orders": 0, "farmed": 0, "errors": 0}

    def start(self):
        """Bắt đầu bot trong background thread."""
        if self._thread and self._thread.is_alive():
            return
        self.running = True
        self.paused = False
        self._thread = threading.Thread(target=self._main_loop, daemon=True)
        self._thread.start()
        self.log("▶️ Bot đã bắt đầu")

    def pause(self):
        """Tạm dừng bot."""
        self.paused = True
        self.log("⏸️ Bot tạm dừng")

    def resume(self):
        """Tiếp tục bot."""
        self.paused = False
        self.log("▶️ Bot tiếp tục")

    def stop(self):
        """Dừng bot."""
        self.running = False
        self.paused = False
        self.log("⏹️ Bot đã dừng")

    def restart(self):
        """Khởi động lại bot."""
        self.stop()
        time.sleep(1)
        self.stats = {"orders": 0, "farmed": 0, "errors": 0}
        self.start()
        self.log("🔄 Bot đã khởi động lại")

    def _main_loop(self):
        """Vòng lặp chính."""
        while self.running:
            if self.paused:
                time.sleep(1)
                continue

            try:
                self.log("=" * 30)
                self.log("🔄 BẮT ĐẦU CHU KỲ")

                # Bước 1: Giao đơn
                self._process_orders()

                if not self.running:
                    break

                # Bước 2: Trồng & Thu hoạch
                self._smart_farm()

                self.log(f"📊 Đơn: {self.stats['orders']} | Farm: {self.stats['farmed']}")

                # Chờ 3 phút
                self.log("⏳ Chờ 3 phút...")
                for _ in range(180):
                    if not self.running:
                        return
                    if self.paused:
                        while self.paused and self.running:
                            time.sleep(1)
                    time.sleep(1)

            except Exception as e:
                self.log(f"❌ Lỗi: {e}")
                self.stats["errors"] += 1
                time.sleep(5)

    # ----------------------------------------------------------
    # GIAO ĐƠN
    # ----------------------------------------------------------
    def _process_orders(self):
        self.log("📦 Kiểm tra đơn hàng...")
        screenshot = self.ctrl.screenshot()
        if screenshot is None:
            return

        # Tìm dấu chấm than đỏ
        reds = self.matcher.find_all(screenshot, DAU_CHAM_THAN_DO_IMG)
        # Tìm dấu chấm than vàng
        yellows = self.matcher.find_all(screenshot, DAU_CHAM_THAN_VANG_IMG)

        all_marks = [(x, y, c, "red") for x, y, c in reds] + \
                    [(x, y, c, "yellow") for x, y, c in yellows]

        if not all_marks:
            self.log("  Không có đơn hàng")
            return

        self.log(f"  Tìm thấy {len(all_marks)} dấu (!)")

        for x, y, conf, color in all_marks:
            if not self.running or self.paused:
                return

            self.ctrl.tap(x, y)
            self.log(f"  Click (!) {color} ({x}, {y})")
            time.sleep(DELAY_STEP)

            ss = self.ctrl.screenshot()
            if ss is None:
                continue

            # Kiểm tra nút Đến làm
            btn = self.matcher.find(ss, BTN_DEN_LAM)
            if btn:
                self.ctrl.tap(btn[0], btn[1])
                self.log("  🔨 Đến làm")
                time.sleep(DELAY_STEP)
                self.ctrl.tap(445, 1477)  # Nút Làm
                self.log("  ✅ Làm")
                time.sleep(DELAY_STEP)
                self.ctrl.tap(450, 800)  # Tap ngoài popup
                time.sleep(DELAY_STEP)

                ss2 = self.ctrl.screenshot()
                if ss2:
                    giao = self.matcher.find(ss2, BTN_GIAO)
                    if giao:
                        self.ctrl.tap(giao[0], giao[1])
                        self.log("  📦 Giao hàng")
                        time.sleep(DELAY_STEP)
                        self.ctrl.tap(450, 800)  # Đóng popup thưởng
                        time.sleep(DELAY_STEP)

                self.stats["orders"] += 1
                continue

            # Kiểm tra nút Chưa có hàng
            btn = self.matcher.find(ss, BTN_CHUA_CO_HANG)
            if btn:
                self.ctrl.tap(btn[0], btn[1])
                self.log("  ⏭️ Chưa có hàng")
                time.sleep(DELAY_STEP)
                self.stats["orders"] += 1
                continue

            # Kiểm tra nút Giao
            btn = self.matcher.find(ss, BTN_GIAO)
            if btn:
                self.ctrl.tap(btn[0], btn[1])
                self.log("  📦 Giao hàng")
                time.sleep(DELAY_STEP)
                self.ctrl.tap(450, 800)
                time.sleep(DELAY_STEP)
                self.stats["orders"] += 1

    # ----------------------------------------------------------
    # TRỒNG & THU HOẠCH
    # ----------------------------------------------------------
    def _smart_farm(self):
        self.log("🌱 Trồng & Thu hoạch...")

        for idx, (px, py) in enumerate(FARM_PLOTS):
            self.log(f"  --- Ô #{idx + 1} ({px}, {py}) ---")

            while self.running and not self.paused:
                self.ctrl.tap(px, py)
                self.log(f"  Tap ô đất")
                time.sleep(DELAY_STEP)

                screenshot = self.ctrl.screenshot()
                if screenshot is None:
                    break

                has_harvest = self.matcher.find(screenshot, THU_HOACH_NHANH_IMG)
                has_menu = self.matcher.find(screenshot, POPUP_MENU_IMG)

                if has_harvest:
                    hx, hy, conf = has_harvest
                    self.ctrl.tap(hx, hy)
                    self.log(f"  ⚡ Thu hoạch ({hx},{hy}) conf={conf:.3f}")
                    self.stats["farmed"] += 1
                    time.sleep(DELAY_STEP)

                elif has_menu:
                    fx, fy = FARM_FIRST_FLOWER
                    self.ctrl.tap(fx, fy)
                    self.log(f"  🌸 Chọn hoa")
                    time.sleep(DELAY_STEP)

                    self.ctrl.tap(px, py)
                    time.sleep(DELAY_STEP)
                    vx, vy = FARM_VIP_BUTTON
                    self.ctrl.tap(vx, vy)
                    self.log(f"  ⚡ Tưới nhanh")
                    time.sleep(DELAY_STEP)
                    self.stats["farmed"] += 1

                else:
                    self.ctrl.tap(798, 624)
                    self.log(f"  ⏭️ Đóng popup")
                    time.sleep(DELAY_STEP)
                    break

            self.log(f"  ✅ Xong ô #{idx + 1}")
