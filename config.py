# ============================================================
# CẤU HÌNH CHƯƠNG TRÌNH AUTO GAME - THẾ GIỚI HOA VIÊN CỦA TÔI
# ============================================================

import os

# --- Kết nối ADB (LDPlayer) ---
ADB_HOST = "127.0.0.1"
ADB_PORT = 5555  # Port mặc định LDPlayer instance 1. Instance 2 = 5557, 3 = 5559...

# --- Đường dẫn ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Tạo thư mục nếu chưa có
for d in [IMAGES_DIR, SCREENSHOTS_DIR, LOG_DIR]:
    os.makedirs(d, exist_ok=True)

# Thư mục ảnh mẫu theo chức năng
IMAGES_BUTTONS = os.path.join(IMAGES_DIR, "buttons")    # Ảnh các nút bấm
IMAGES_ORDERS = os.path.join(IMAGES_DIR, "orders")      # Ảnh đơn hàng
IMAGES_UI = os.path.join(IMAGES_DIR, "ui")              # Ảnh UI chung

for d in [IMAGES_BUTTONS, IMAGES_ORDERS, IMAGES_UI]:
    os.makedirs(d, exist_ok=True)

# --- Độ phân giải màn hình LDPlayer (chế độ dọc) ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 1600

# --- Ngưỡng nhận diện ảnh (OpenCV template matching) ---
MATCH_THRESHOLD = 0.8  # 0.0 - 1.0, càng cao càng chính xác

# --- Thời gian chờ (giây) ---
DELAY_TAP = 0.3           # Chờ sau mỗi lần tap
DELAY_BETWEEN_ACTIONS = 1.0  # Chờ giữa các hành động
DELAY_SCREEN_LOAD = 2.0     # Chờ màn hình load
DELAY_ORDER = 1.0           # Chờ khi xử lý đơn hàng

# --- Vị trí các nút UI cố định (900x1600) ---
UI_POSITIONS = {
    "btn_hoa_tuoi": (75, 1540),      # Nút Hoa Tươi (dưới trái)
    "btn_ban": (210, 1540),           # Nút Bạn
    "btn_hoi": (340, 1540),           # Nút Hội
    "btn_noi_dung": (50, 980),        # Nút Nội Dung (cuộn giấy)
    "btn_close": (850, 50),           # Nút đóng/X
    "btn_confirm": (450, 800),        # Nút xác nhận
    "btn_cancel": (300, 800),         # Nút hủy
}

# --- Cấu hình trồng cây ---
# Tọa độ ô đất trống (có thể thêm nhiều ô)
FARM_PLOTS = [
    (533, 1396),
]

# Tọa độ hoa đầu tiên trong menu trồng cây
FARM_FIRST_FLOWER = (90, 960)

# Tọa độ nút VIP (Tưới nhanh / Thu hoạch nhanh) - cùng vị trí
FARM_VIP_BUTTON = (628, 1179)

# --- Cấu hình đơn hàng ---
MAX_ORDER_RETRY = 3        # Số lần thử lại khi giao đơn thất bại
ORDER_CHECK_INTERVAL = 60  # Kiểm tra đơn mới mỗi X giây

# --- Cấu hình vòng lặp chính ---
MAIN_LOOP_INTERVAL = 5     # Giây giữa mỗi vòng lặp kiểm tra
MAX_RUNTIME_HOURS = 8      # Tự dừng sau X giờ
