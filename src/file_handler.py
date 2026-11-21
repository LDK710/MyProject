import json
from pathlib import Path
from src.config import ENCODING

def save_json(data: dict | list, file_path: str | Path) -> bool:
    """Lưu dữ liệu (dict/list) ra file JSON. Tự tạo thư mục nếu chưa có."""
    path = Path(file_path)
    try:
        # Tự động tạo thư mục cha (ví dụ thư mục data/) nếu chưa tồn tại
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with path.open("w", encoding=ENCODING) as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"[Thành công] Đã lưu dữ liệu vào: {path}")
        return True
    except Exception as e:
        print(f"[Lỗi khi lưu JSON] {e}")
        return False

def load_json(file_path: str | Path) -> dict | list | None:
    """Đọc dữ liệu từ file JSON. Trả về dict/list hoặc None nếu lỗi."""
    path = Path(file_path)
    try:
        with path.open("r", encoding=ENCODING) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[Lỗi] Không tìm thấy file JSON tại: {path}")
        return None
    except json.JSONDecodeError:
        print(f"[Lỗi] File '{path}' bị sai định dạng JSON!")
        return None