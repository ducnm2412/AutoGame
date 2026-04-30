# ============================================================
# TEST - Giao hàng (Order)
# ============================================================

import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from core.adb_controller import ADBController
from core.image_matcher import ImageMatcher
from handlers.popup_handler import PopupHandler
from handlers.order_handler import OrderHandler
from core.logger import setup_logger

logger = setup_logger()


def test():
    logger.info("=" * 50)
    logger.info("TEST: GIAO HÀNG")
    logger.info("=" * 50)

    adb = ADBController()
    if not adb.connect():
        return

    matcher = ImageMatcher()
    popup = PopupHandler(adb, matcher)
    order = OrderHandler(adb, matcher, popup)

    count = order.process_orders()
    logger.info(f"Kết quả giao hàng: {count} đơn đã xử lý")

    adb.disconnect()
    logger.info("DONE")


if __name__ == "__main__":
    test()
