# ============================================================
# TEST THU HOẠCH - Chỉ thu hoạch (không trồng/tưới)
# ============================================================

from core.adb_controller import ADBController
from core.logger import setup_logger
from handlers.farm_handler import FarmHandler

logger = setup_logger()


def main():
    logger.info("=" * 50)
    logger.info("TEST: THU HOẠCH")
    logger.info("=" * 50)

    adb = ADBController()
    if not adb.connect():
        logger.error("Không kết nối được!")
        return

    farm = FarmHandler(adb)
    count = farm.harvest_only()
    logger.info(f"Kết quả: {count} ô đã thu hoạch")

    adb.disconnect()
    logger.info("DONE")


if __name__ == "__main__":
    main()
