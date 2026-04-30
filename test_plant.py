# ============================================================
# TEST - Thu hoach
# ============================================================

import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from core.adb_controller import ADBController
from core.image_matcher import ImageMatcher
from handlers.farm_handler import FarmHandler
from core.logger import setup_logger

logger = setup_logger()


def test():
    logger.info("=" * 50)
    logger.info("TEST: THU HOACH")
    logger.info("=" * 50)

    adb = ADBController()
    if not adb.connect():
        return

    farm = FarmHandler(adb, ImageMatcher())
    count = farm.harvest()
    logger.info(f"Ket qua thu hoach: {count}")

    adb.disconnect()
    logger.info("DONE")


if __name__ == "__main__":
    test()
