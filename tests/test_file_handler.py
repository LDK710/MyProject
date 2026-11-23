import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import BASE_DIR
from src.file_handler import save_json, load_json

class TestFileHandler(unittest.TestCase):
    def setUp(self):
        self.temp_file = BASE_DIR / "data" / "temp_test_io.json"
        self.sample_data = {
            "project": "RAG Chatbot",
            "pages": [{"page": 1, "text": "Kiểm thử tiếng Việt có dấu"}]
        }

    def tearDown(self):
        # Xóa file tạm sau khi chạy xong test
        if self.temp_file.exists():
            self.temp_file.unlink()

    def test_save_and_load_json(self):
        # 1. Test lưu file
        is_saved = save_json(self.sample_data, self.temp_file)
        self.assertTrue(is_saved)
        self.assertTrue(self.temp_file.exists())

        # 2. Test đọc lại file
        loaded_data = load_json(self.temp_file)
        self.assertEqual(loaded_data, self.sample_data)

    def test_load_non_existent_file(self):
        result = load_json(BASE_DIR / "data" / "khong_ton_tai.json")
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()