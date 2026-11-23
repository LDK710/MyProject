import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.text_cleaner import clean_text, remove_empty_pages, validate_document

class TestTextCleaner(unittest.TestCase):
    def test_clean_text(self):
        dirty_text = "   Xin   chào\t\tthế giới!\n\n\n\nĐây là   đoạn 2.   "
        expected = "Xin chào thế giới!\nĐây là đoạn 2."
        self.assertEqual(clean_text(dirty_text), expected)

    def test_remove_empty_pages(self):
        raw_pages = [
            {"page": 1, "text": "   \n\t  "},           # Rỗng -> bị loại
            {"page": 2, "text": "12"},                  # Quá ngắn (<= 5 ký tự) -> bị loại
            {"page": 3, "text": "Nội dung trang 3 hợp lệ."} # Giữ lại
        ]
        cleaned = remove_empty_pages(raw_pages)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0]["page"], 3)

    def test_validate_document(self):
        valid_docs = [{"page": 1, "text": "Hợp lệ"}]
        is_ok, _ = validate_document(valid_docs)
        self.assertTrue(is_ok)

        invalid_docs = [{"page": 1}]  # Thiếu key 'text'
        is_ok_fail, msg = validate_document(invalid_docs)
        self.assertFalse(is_ok_fail)
        self.assertIn("thiếu trường", msg)

if __name__ == "__main__":
    unittest.main()