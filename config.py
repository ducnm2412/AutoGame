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
IMAGES_CROPS = os.path.join(IMAGES_DIR, "crops")        # Ảnh các loại cây
IMAGES_BUTTONS = os.path.join(IMAGES_DIR, "buttons")    # Ảnh các nút bấm
IMAGES_ORDERS = os.path.join(IMAGES_DIR, "orders")      # Ảnh đơn hàng
IMAGES_UI = os.path.join(IMAGES_DIR, "ui")              # Ảnh UI chung

for d in [IMAGES_CROPS, IMAGES_BUTTONS, IMAGES_ORDERS, IMAGES_UI]:
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
DELAY_HARVEST = 0.5         # Chờ sau khi thu hoạch 1 ô
DELAY_PLANT = 0.5           # Chờ sau khi trồng 1 ô
DELAY_ORDER = 1.0           # Chờ khi xử lý đơn hàng

# --- Vị trí cố định các ô trồng cây (tọa độ x, y) ---
# Tọa độ dựa trên screenshot 900x1600 (chế độ dọc)
# Các ô đất trống nằm ở vùng dưới-trái của màn hình
FARM_PLOTS = [
    # Vị trí ô đất trống (đã test OK - mở được menu trồng)
    (180, 670),
    (120, 770),
]

# --- Danh sách cây trồng ---
# key: tên cây, value: dict chứa thông tin
# - image: tên file ảnh mẫu trong thư mục images/crops/
# - grow_time: thời gian trồng (phút)
# - priority: độ ưu tiên (số nhỏ = ưu tiên cao)
CROPS = {
    "lua_mi": {
        "image": "lua_mi.png",
        "grow_time": 2,
        "priority": 1,
    },
    "bap": {
        "image": "bap.png",
        "grow_time": 5,
        "priority": 2,
    },
    "ca_rot": {
        "image": "ca_rot.png",
        "grow_time": 10,
        "priority": 3,
    },
    "ca_chua": {
        "image": "ca_chua.png",
        "grow_time": 20,
        "priority": 4,
    },
    "dau": {
        "image": "dau.png",
        "grow_time": 30,
        "priority": 5,
    },
    "mia": {
        "image": "mia.png",
        "grow_time": 60,
        "priority": 6,
    },
}

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

# --- Cấu hình đơn hàng ---
MAX_ORDER_RETRY = 3        # Số lần thử lại khi giao đơn thất bại
ORDER_CHECK_INTERVAL = 60  # Kiểm tra đơn mới mỗi X giây

# --- Cấu hình vòng lặp chính ---
MAIN_LOOP_INTERVAL = 5     # Giây giữa mỗi vòng lặp kiểm tra
MAX_RUNTIME_HOURS = 8      # Tự dừng sau X giờ
