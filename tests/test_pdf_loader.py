import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.pdf_loader import extract_pdf

class TestPdfLoader(unittest.TestCase):
    @patch("src.pdf_loader.os.getenv", return_value="fake-api-key")
    @patch("builtins.open", new_callable=mock_open, read_data=b"%PDF-1.4 fake content")
    @patch("src.pdf_loader.requests.post")
    @patch("src.pdf_loader.requests.get")
    def test_extract_pdf_success(self, mock_get, mock_post, mock_file, mock_env):
        # 1. Giả lập phản hồi bước Upload
        mock_post_res = MagicMock()
        mock_post_res.status_code = 200
        mock_post_res.json.return_value = {"id": "job-12345"}
        mock_post.return_value = mock_post_res

        # 2. Giả lập phản hồi bước Polling & trả về Markdown
        mock_get_res = MagicMock()
        mock_get_res.status_code = 200
        mock_get_res.json.return_value = {
            "job": {"status": "COMPLETED"},
            "markdown": {
                "pages": [
                    {"page_number": 1, "markdown": "# Tiêu đề trang 1\nNội dung mẫu."}
                ]
            }
        }
        mock_get.return_value = mock_get_res

        # 3. Chạy thử hàm extract_pdf
        result = extract_pdf("dummy.pdf")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["page"], 1)
        self.assertIn("# Tiêu đề trang 1", result[0]["text"])

if __name__ == "__main__":
    unittest.main()