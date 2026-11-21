from pathlib import Path

# Xác định thư mục gốc của dự án (MyProject)
BASE_DIR = Path(__file__).resolve().parent.parent

# Thư mục lưu trữ dữ liệu đầu vào / đầu ra
DATA_DIR = BASE_DIR / "data"

# Bảng mã mặc định
ENCODING = "utf-8"