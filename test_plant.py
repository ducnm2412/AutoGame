# ============================================================
# TEST - Trồng cây (Trồng → Tưới nhanh → Thu hoạch nhanh)
# ============================================================

import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from core.adb_controller import ADBController
from handlers.farm_handler import FarmHandler
from core.logger import setup_logger

logger = setup_logger()


def test():
    logger.info("=" * 50)
    logger.info("TEST: TRỒNG CÂY")
    logger.info("=" * 50)

    adb = ADBController()
    if not adb.connect():
        return

    farm = FarmHandler(adb)
    count = farm.run()
    logger.info(f"Kết quả: {count} ô đã trồng & thu hoạch")

    adb.disconnect()
    logger.info("DONE")


if __name__ == "__main__":
    test()
