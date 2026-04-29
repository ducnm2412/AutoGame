# ============================================================
# GAME BOT - ORCHESTRATOR
# Điều phối các handler: Farm → Orders
# ============================================================

import time
from core.adb_controller import ADBController
from core.image_matcher import ImageMatcher
from core.logger import setup_logger
from handlers.popup_handler import PopupHandler
from handlers.order_handler import OrderHandler
from handlers.farm_handler import FarmHandler
from config import DELAY_BETWEEN_ACTIONS

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
        self.farm = FarmHandler(self.adb, self.matcher)

        # Stats
        self.stats = {
            "harvested": 0,
            "planted": 0,
            "orders_done": 0,
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
        """Chạy 1 chu kỳ: Thu hoạch → Trồng → Đơn hàng."""
        logger.info("=" * 40)
        logger.info("🔄 BẮT ĐẦU CHU KỲ MỚI")
        logger.info("=" * 40)

        try:
            # Bước 1: Thu hoạch
            if self.farm.has_harvest_template():
                count = self.farm.harvest()
                self.stats["harvested"] += count
                time.sleep(DELAY_BETWEEN_ACTIONS)
            else:
                logger.info("⏭️ Bỏ qua thu hoạch (chưa có ảnh mẫu)")

            # Bước 2: Trồng cây
            if self.farm.has_crop_templates():
                count = self.farm.plant()
                self.stats["planted"] += count
                time.sleep(DELAY_BETWEEN_ACTIONS)
            else:
                logger.info("⏭️ Bỏ qua trồng cây (chưa có ảnh mẫu)")

            # Bước 3: Xử lý đơn hàng
            count = self.orders.process_orders()
            self.stats["orders_done"] += count

        except Exception as e:
            logger.error(f"Lỗi trong chu kỳ: {e}")
            self.stats["errors"] += 1

        self._print_stats()

    # ----------------------------------------------------------
    # STATS
    # ----------------------------------------------------------
    def _print_stats(self):
        logger.info("--- THỐNG KÊ ---")
        logger.info(f"  Thu hoạch: {self.stats['harvested']}")
        logger.info(f"  Trồng cây: {self.stats['planted']}")
        logger.info(f"  Đơn hàng:  {self.stats['orders_done']}")
        logger.info(f"  Lỗi:       {self.stats['errors']}")
