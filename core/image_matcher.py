# ============================================================
# MODULE NHẬN DIỆN ẢNH - OPENCV TEMPLATE MATCHING
# Hỗ trợ ảnh có alpha channel (xóa nền) với mask matching
# ============================================================

import cv2
import numpy as np
import os
import time
from PIL import Image
from core.logger import setup_logger
from config import MATCH_THRESHOLD

logger = setup_logger()


class ImageMatcher:
    """Nhận diện ảnh bằng OpenCV template matching (hỗ trợ mask)."""

    def __init__(self, threshold=MATCH_THRESHOLD):
        self.threshold = threshold
        self._cache = {}  # cache: path -> (template_bgr, mask_or_None)

    def _load_template(self, path):
        """Load template, tách mask từ alpha channel nếu có."""
        if path in self._cache:
            return self._cache[path]
        if not os.path.exists(path):
            logger.error(f"Không tìm thấy ảnh mẫu: {path}")
            return None, None

        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            logger.error(f"Không đọc được ảnh: {path}")
            return None, None

        mask = None
        if img.shape[2] == 4:
            alpha = img[:, :, 3]
            mask = alpha.copy()
            template = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        else:
            template = img

        self._cache[path] = (template, mask)
        return template, mask

    def _to_cv2(self, img):
        """Chuyển PIL Image sang BGR numpy array."""
        if isinstance(img, Image.Image):
            rgb = img.convert("RGB")
            return cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2BGR)
        return img

    def find(self, screenshot, template_path, threshold=None):
        """Tìm ảnh mẫu, trả về (x, y, confidence) hoặc None."""
        threshold = threshold or self.threshold
        screen = self._to_cv2(screenshot)
        template, mask = self._load_template(template_path)
        if template is None:
            return None

        if template.shape[0] > screen.shape[0] or template.shape[1] > screen.shape[1]:
            return None

        if mask is not None:
            result = cv2.matchTemplate(screen, template, cv2.TM_CCORR_NORMED, mask=mask)
        else:
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)

        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        effective_threshold = threshold if mask is None else max(threshold, 0.98)

        if max_val >= effective_threshold:
            h, w = template.shape[:2]
            cx, cy = max_loc[0] + w // 2, max_loc[1] + h // 2
            logger.debug(f"Found {os.path.basename(template_path)} at ({cx},{cy}) conf={max_val:.3f}")
            return (cx, cy, max_val)
        return None

    def find_all(self, screenshot, template_path, threshold=None):
        """Tìm tất cả vị trí, trả về list[(x,y,conf)]."""
        threshold = threshold or self.threshold
        screen = self._to_cv2(screenshot)
        template, mask = self._load_template(template_path)
        if template is None:
            return []

        if template.shape[0] > screen.shape[0] or template.shape[1] > screen.shape[1]:
            return []

        h, w = template.shape[:2]

        if mask is not None:
            result = cv2.matchTemplate(screen, template, cv2.TM_CCORR_NORMED, mask=mask)
            effective_threshold = max(threshold, 0.98)
        else:
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            effective_threshold = threshold

        locs = np.where(result >= effective_threshold)
        matches = []
        for pt in zip(*locs[::-1]):
            matches.append((pt[0] + w // 2, pt[1] + h // 2, float(result[pt[1], pt[0]])))

        matches.sort(key=lambda m: m[2], reverse=True)
        filtered = []
        for m in matches:
            if not any(abs(m[0]-f[0]) < 30 and abs(m[1]-f[1]) < 30 for f in filtered):
                filtered.append(m)
        return filtered

    def exists(self, screenshot, template_path, threshold=None):
        return self.find(screenshot, template_path, threshold) is not None

    def wait_for(self, adb, template_path, timeout=10, interval=0.5):
        """Chờ ảnh mẫu xuất hiện, trả về vị trí hoặc None."""
        start = time.time()
        while time.time() - start < timeout:
            ss = adb.screenshot()
            if ss:
                r = self.find(ss, template_path)
                if r:
                    return r
            time.sleep(interval)
        logger.warning(f"Timeout chờ {os.path.basename(template_path)}")
        return None

    def find_and_tap(self, adb, template_path, threshold=None, screenshot=None):
        """Tìm và tap vào ảnh mẫu. Trả về True/False."""
        if screenshot is None:
            screenshot = adb.screenshot()
        if screenshot is None:
            return False
        r = self.find(screenshot, template_path, threshold)
        if r:
            adb.tap(r[0], r[1])
            logger.info(f"Tap {os.path.basename(template_path)} at ({r[0]},{r[1]})")
            return True
        return False

    def clear_cache(self):
        self._cache.clear()
