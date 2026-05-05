# ============================================================
# GAME BOT - ORCHESTRATOR
# Điều phối các handler: Orders → Farm (thông minh)
# ============================================================

import time
from core.adb_controller import ADBController
from core.image_matcher import ImageMatcher
from core.logger import setup_logger
from handlers.popup_handler import PopupHandler
from handlers.order_handler import OrderHandler
from handlers.farm_handler import FarmHandler
from config import DELAY_BETWEEN_ACTIONS, ORDER_CHECK_INTERVAL, MAIN_LOOP_INTERVAL

logger = setup_logger()


class GameBot:
    """Bot tự động chơi game Thế Giới Hoa Viên Của Tôi."""

    def __init__(self):
        # Core
        self.adb = ADBController()
        self.matcher = ImageMatcher()
        self.running = False

        # Handlers
        self.popup = PopupHandler(self.adb, self.matcher)
        self.orders = OrderHandler(self.adb, self.matcher, self.popup)
        self.farm = FarmHandler(self.adb)

        # Stats
        self.stats = {
            "orders_done": 0,
            "farmed": 0,
            "errors": 0,
        }

    # ----------------------------------------------------------
    # LIFECYCLE
    # ----------------------------------------------------------
    def start(self):
        """Khởi động bot."""
        logger.info("=" * 50)
        logger.info("🌱 KHỞI ĐỘNG AUTO GAME - THẾ GIỚI HOA VIÊN")
        logger.info("=" * 50)

        if not self.adb.connect():
            logger.error("Không thể kết nối LDPlayer!")
            return False

        if not self.adb.is_device_ready():
            logger.error("Thiết bị không sẵn sàng!")
            return False

        w, h = self.adb.get_screen_size()
        logger.info(f"Màn hình: {w}x{h}")
        self.running = True
        return True

    def stop(self):
        """Dừng bot."""
        self.running = False
        self.adb.disconnect()
        logger.info("🛑 Bot đã dừng")
        self._print_stats()

    # ----------------------------------------------------------
    # VÒNG LẶP CHÍNH
    # ----------------------------------------------------------
    def run_cycle(self):
        """Chạy 1 chu kỳ: Đơn hàng → Trồng & Thu hoạch (thông minh)."""
        logger.info("=" * 40)
        logger.info("🔄 BẮT ĐẦU CHU KỲ MỚI")
        logger.info("=" * 40)

        try:
            # Bước 1: Xử lý đơn hàng
            count = self.orders.process_orders()
            self.stats["orders_done"] += count
            time.sleep(DELAY_BETWEEN_ACTIONS)

            # Bước 2: Trồng & Thu hoạch thông minh
            # (tap ô đất → nhận diện → thu hoạch nếu có, trồng mới nếu trống)
            count = self.farm.run()
            self.stats["farmed"] += count

        except Exception as e:
            logger.error(f"Lỗi trong chu kỳ: {e}")
            self.stats["errors"] += 1

        self._print_stats()

    def wait_and_check_orders(self):
        """
        Chờ MAIN_LOOP_INTERVAL giây, trong khi chờ kiểm tra đơn hàng
        mỗi ORDER_CHECK_INTERVAL giây.
        """
        waited = 0
        interval = ORDER_CHECK_INTERVAL
        remaining = MAIN_LOOP_INTERVAL

        logger.info(f"⏳ Chờ {remaining}s, kiểm tra đơn hàng mỗi {interval}s...")

        while waited < remaining and self.running:
            time.sleep(interval)
            waited += interval

            if not self.running:
                break

            try:
                logger.info(f"📦 Kiểm tra đơn hàng... ({waited}/{remaining}s)")
                count = self.orders.process_orders()
                self.stats["orders_done"] += count
            except Exception as e:
                logger.error(f"Lỗi kiểm tra đơn: {e}")
                self.stats["errors"] += 1

        logger.info("⏳ Hết thời gian chờ, bắt đầu chu kỳ mới")

    # ----------------------------------------------------------
    # STATS
    # ----------------------------------------------------------
    def _print_stats(self):
        logger.info("--- THỐNG KÊ ---")
        logger.info(f"  Đơn hàng:    {self.stats['orders_done']}")
        logger.info(f"  Trồng/hoạch: {self.stats['farmed']}")
        logger.info(f"  Lỗi:         {self.stats['errors']}")
