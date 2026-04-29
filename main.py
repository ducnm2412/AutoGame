# ============================================================
# MAIN - Entry Point
# ============================================================

import sys
import time

# Fix encoding cho Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from core.bot import GameBot
from config import MAIN_LOOP_INTERVAL


def run_continuous():
    """Chạy bot liên tục."""
    bot = GameBot()
    if not bot.start():
        return

    print("Bot chạy liên tục... Ctrl+C để dừng")
    try:
        while bot.running:
            bot.run_cycle()
            time.sleep(MAIN_LOOP_INTERVAL)
    except KeyboardInterrupt:
        print("\nĐang dừng bot...")
    finally:
        bot.stop()


def run_single():
    """Chạy bot 1 chu kỳ."""
    bot = GameBot()
    if not bot.start():
        return
    bot.run_cycle()
    bot.stop()


def main():
    print("=" * 50)
    print("  🌸 AUTO GAME - THẾ GIỚI HOA VIÊN CỦA TÔI")
    print("=" * 50)
    print()
    print("  1. Chạy liên tục (khuyên dùng)")
    print("  2. Chạy 1 chu kỳ")
    print("  0. Thoát")
    print()

    choice = input("Chọn chế độ: ").strip()

    if choice == "1":
        run_continuous()
    elif choice == "2":
        run_single()
    elif choice == "0":
        print("Thoát!")
    else:
        print("Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()
